import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt


# ==========================================
# 1. Mathematical Core: Poincaré Ball Model
# ==========================================

class PoincareDistance(nn.Module):
    """
    Calculates the distance in the Poincaré Ball model.
    Formula: arccosh(1 + 2 * ||u-v||^2 / ((1-||u||^2)(1-||v||^2)))
    """

    def __init__(self, eps=1e-5):
        super().__init__()
        self.eps = eps

    def forward(self, u, v):
        # Squared Euclidean distance
        sq_dist = torch.sum((u - v) ** 2, dim=-1)

        # Norms
        u_sq = torch.sum(u ** 2, dim=-1)
        v_sq = torch.sum(v ** 2, dim=-1)

        # Boundary constraints to avoid division by zero
        u_sq = torch.clamp(u_sq, max=1 - self.eps)
        v_sq = torch.clamp(v_sq, max=1 - self.eps)

        # The Mobility Factor
        alpha = 1 - u_sq
        beta = 1 - v_sq

        # The Core Formula
        gamma = 1 + 2 * sq_dist / (alpha * beta)

        # Arccosh(x) = ln(x + sqrt(x^2 - 1))
        # We clamp gamma to >= 1 + eps for numerical stability
        gamma = torch.clamp(gamma, min=1 + self.eps)
        dist = torch.acosh(gamma)

        return dist


# ==========================================
# 2. The Embedding Model
# ==========================================

class HyperbolicTreeLearner(nn.Module):
    def __init__(self, num_nodes, embedding_dim=2):
        super().__init__()
        # Initialize weights randomly near the origin (0,0)
        # In Hyperbolic space, the origin represents the "Root" of the tree.
        self.embeddings = nn.Embedding(num_nodes, embedding_dim)

        # Initialize with small values (close to root)
        nn.init.uniform_(self.embeddings.weight, -0.001, 0.001)

        self.distance_fn = PoincareDistance()

    def forward(self, idx_u, idx_v):
        u = self.embeddings(idx_u)
        v = self.embeddings(idx_v)
        return self.distance_fn(u, v)

    def project_embeddings(self):
        """
        CRITICAL: Projects embeddings back into the unit ball if they drift out.
        We scale any vector with norm >= 1 to have norm = 1 - epsilon.
        """
        with torch.no_grad():
            norms = torch.norm(self.embeddings.weight, p=2, dim=-1, keepdim=True)
            max_norm = 1.0 - 1e-5
            cond = norms > max_norm
            projected = self.embeddings.weight / norms * max_norm
            self.embeddings.weight.where(cond, projected)


# ==========================================
# 3. Data Simulation (Logical Structure)
# ==========================================

# Let's map a logical structure of an article
# 0: "Article Title" (Root)
# 1: "Introduction"
# 2: "Argument A"
# 3: "Argument B"
# 4: "Evidence A.1"
# 5: "Evidence A.2"

node_names = {
    0: "ROOT: Article",
    1: "Intro",
    2: "Sec: Theory",
    3: "Sec: Application",
    4: "Sub: Math",
    5: "Sub: Code"
}

# Positive pairs: (Parent, Child) - These should be close
pos_edges = [
    (0, 1),  # Root -> Intro
    (0, 2),  # Root -> Theory
    (0, 3),  # Root -> Application
    (2, 4),  # Theory -> Math
    (3, 5)  # Application -> Code
]

# Negative pairs: (Unrelated nodes) - These should be far apart
# Randomly sampling unconnected nodes improves the geometry
neg_edges = [
    (1, 4), (1, 5), (2, 3), (4, 5)
]

# ==========================================
# 4. Training Loop
# ==========================================

model = HyperbolicTreeLearner(num_nodes=len(node_names), embedding_dim=2)
optimizer = optim.Adam(model.parameters(), lr=0.01)

print("Training Hyperbolic Embeddings...")

for epoch in range(500):
    optimizer.zero_grad()

    # 1. Positive Loss: Minimize distance between connected nodes
    u_pos = torch.tensor([x[0] for x in pos_edges])
    v_pos = torch.tensor([x[1] for x in pos_edges])
    pos_dists = model(u_pos, v_pos)
    loss_pos = pos_dists.mean()  # We want this small

    # 2. Negative Loss: Maximize distance between unconnected nodes
    # We use a Margin Loss: max(0, margin - dist)
    u_neg = torch.tensor([x[0] for x in neg_edges])
    v_neg = torch.tensor([x[1] for x in neg_edges])
    neg_dists = model(u_neg, v_neg)
    loss_neg = torch.relu(2.0 - neg_dists).mean()  # Push apart until dist is 2.0

    loss = loss_pos + loss_neg

    loss.backward()
    optimizer.step()

    # 3. Riemannian Projection (Constraint)
    model.project_embeddings()

    if epoch % 100 == 0:
        print(f"Epoch {epoch}: Loss {loss.item():.4f}")

# ==========================================
# 5. Result: Reconstructing the Tree
# ==========================================

print("\n--- INFERRED HIERARCHY ---")
# In Poincaré space, the magnitude (norm) of the vector determines the hierarchy level.
# Origin (0,0) = Root (Top level)
# Boundary (norm -> 1) = Leaves (Bottom level)

embeddings = model.embeddings.weight.detach().numpy()
norms = np.linalg.norm(embeddings, axis=1)

# Sort nodes by their distance to the center
sorted_indices = np.argsort(norms)

for idx in sorted_indices:
    name = node_names[idx]
    norm = norms[idx]
    # Simple visual indentation based on norm
    indent = "  " * int(norm * 5)
    print(f"{indent}- {name} (r={norm:.4f})")

# ==========================================
# 6. Visualization (Optional)
# ==========================================
# Plotting the Poincaré Disk
fig, ax = plt.subplots(figsize=(6, 6))
circle = plt.Circle((0, 0), 1, color='b', fill=False, linestyle='--')
ax.add_artist(circle)

# Plot nodes
ax.scatter(embeddings[:, 0], embeddings[:, 1], c='red')
for i, txt in enumerate(node_names):
    ax.annotate(node_names[i], (embeddings[i, 0], embeddings[i, 1]))

# Plot edges
for u, v in pos_edges:
    p1 = embeddings[u]
    p2 = embeddings[v]
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'k-', alpha=0.5)

ax.set_xlim(-1.1, 1.1)
ax.set_ylim(-1.1, 1.1)
ax.set_aspect('equal')
plt.title("Logical Structure in Poincaré Disk")
plt.grid(False)
# plt.show() # Uncomment to view if running locally