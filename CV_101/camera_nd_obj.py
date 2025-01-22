import numpy as np

class Camera:
    def __init__(self, position=np.array([2, -4, 2]), up=np.array([0, 0, 1]), size=0.3):
        """
        Initialize camera parameters
        
        Args:
            position (np.ndarray): Camera position in 3D space
            up (np.ndarray): Camera up vector
            size (float): Size of camera frustum
        """
        self._position = position
        self._up = up
        self._size = size
        self._direction = None
        self._right = None
        self._vertices = None
        
    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, value):
        self._position = np.array(value)
        self._update_camera()
        
    @property
    def size(self):
        return self._size
    
    @size.setter
    def size(self, value):
        self._size = value
        self._update_camera()
    
    def look_at(self, target):
        """Update camera direction to look at target"""
        self._direction = target - self.position
        self._direction = self._direction / np.linalg.norm(self._direction)
        self._update_camera()
    
    def _update_camera(self):
        """Update camera coordinate system"""
        if self._direction is None:
            return
            
        self._right = np.cross(self._direction, self._up)
        self._right = self._right / np.linalg.norm(self._right)
        self._up = np.cross(self._right, self._direction)
        self._up = self._up / np.linalg.norm(self._up)
        
        self._update_vertices()
    
    def _update_vertices(self):
        """Calculate camera frustum vertices"""
        self._vertices = np.array([
            self.position,  # Apex
            self.position + self.size * (-self._right + self._direction - self._up),
            self.position + self.size * (self._right + self._direction - self._up),
            self.position + self.size * (self._right + self._direction + self._up),
            self.position + self.size * (-self._right + self._direction + self._up)
        ])
    
    def draw(self, ax):
        """Draw camera frustum"""
        if self._vertices is None:
            return
            
        # Draw edges from apex to base
        for i in range(1, 5):
            ax.plot3D([self._vertices[0][0], self._vertices[i][0]],
                     [self._vertices[0][1], self._vertices[i][1]],
                     [self._vertices[0][2], self._vertices[i][2]], 'g-')
        
        # Draw base
        base_indices = [1, 2, 3, 4, 1]
        ax.plot3D([self._vertices[i][0] for i in base_indices],
                 [self._vertices[i][1] for i in base_indices],
                 [self._vertices[i][2] for i in base_indices], 'g-')
        
        # Draw camera position marker
        ax.scatter3D(self.position[0], self.position[1], self.position[2], 
                    c='green', marker='o')

class Cube:
    def __init__(self, origin=np.array([0, 0, 0]), size=1):
        """
        Initialize cube parameters
        
        Args:
            origin (np.ndarray): Origin point of cube
            size (float): Size of cube edges
        """
        self._origin = np.array(origin)
        self._size = size
        self._vertices = None
        self._edges = None
        self._update_geometry()
    
    @property
    def center(self):
        return self._origin + self._size/2
    
    def _update_geometry(self):
        """Update cube vertices and edges"""
        o = self._origin
        s = self._size
        
        # Create vertices
        self._vertices = np.array([
            o + [0,0,0], o + [s,0,0], o + [0,s,0], o + [s,s,0],
            o + [0,0,s], o + [s,0,s], o + [0,s,s], o + [s,s,s]
        ])
        
        # Define edges as pairs of vertex indices
        edge_indices = [
            (0,1), (0,2), (0,4), (1,3), (1,5), (2,3),
            (2,6), (4,5), (4,6), (7,3), (7,5), (7,6)
        ]
        
        # Create edges using vertex coordinates
        self._edges = []
        for start_idx, end_idx in edge_indices:
            self._edges.append([
                self._vertices[start_idx],
                self._vertices[end_idx]
            ])
    
    def draw(self, ax):
        """Draw cube"""
        # Draw vertices
        ax.scatter3D(self._vertices[:, 0], self._vertices[:, 1], 
                    self._vertices[:, 2], c='blue', marker='o')
        
        # Draw edges
        for edge in self._edges:
            start, end = edge
            ax.plot3D([start[0], end[0]],
                     [start[1], end[1]],
                     [start[2], end[2]], c='red')

class Plane:
    def __init__(self, center=[0,0,0], rotation=[0,0,0], scale=5, num_points=10):
        """
        Initialize plane parameters
        
        Args:
            center (list): Center position of plane
            rotation (list): Rotation angles in degrees [rx,ry,rz]
            scale (float): Size of plane
            num_points (int): Resolution of plane grid
        """
        self._center = np.array(center)
        self._rotation = np.array(rotation)
        self._scale = scale
        self._num_points = num_points
        self._surface = None
        self._update_geometry()
    
    @property
    def center(self):
        return self._center
    
    @center.setter
    def center(self, value):
        self._center = np.array(value)
        self._update_geometry()
    
    @property
    def rotation(self):
        return self._rotation
    
    @rotation.setter
    def rotation(self, value):
        self._rotation = np.array(value)
        self._update_geometry()
    
    def _update_geometry(self):
        """Update plane geometry"""
        x_plane = np.linspace(-self._scale, self._scale, self._num_points)
        y_plane = np.linspace(-self._scale, self._scale, self._num_points)
        X_plane, Y_plane = np.meshgrid(x_plane, y_plane)
        Z_plane = np.zeros_like(X_plane)
        
        points = np.stack([X_plane.flatten(), Y_plane.flatten(), 
                          Z_plane.flatten(), np.ones_like(X_plane.flatten())])
        
        # Create transformation matrices
        rx, ry, rz = np.radians(self._rotation)
        Rx = np.array([[1, 0, 0, 0],
                      [0, np.cos(rx), -np.sin(rx), 0],
                      [0, np.sin(rx), np.cos(rx), 0],
                      [0, 0, 0, 1]])
        
        Ry = np.array([[np.cos(ry), 0, np.sin(ry), 0],
                      [0, 1, 0, 0],
                      [-np.sin(ry), 0, np.cos(ry), 0],
                      [0, 0, 0, 1]])
        
        Rz = np.array([[np.cos(rz), -np.sin(rz), 0, 0],
                      [np.sin(rz), np.cos(rz), 0, 0],
                      [0, 0, 1, 0],
                      [0, 0, 0, 1]])
        
        T = np.array([[1, 0, 0, self._center[0]],
                     [0, 1, 0, self._center[1]],
                     [0, 0, 1, self._center[2]],
                     [0, 0, 0, 1]])
        
        transform = T @ Rz @ Ry @ Rx
        transformed = transform @ points
        
        self._surface = (
            transformed[0].reshape(self._num_points, self._num_points),
            transformed[1].reshape(self._num_points, self._num_points),
            transformed[2].reshape(self._num_points, self._num_points)
        )
    
    def draw(self, ax, color='yellow', alpha=0.5):
        """Draw plane"""
        if self._surface is not None:
            ax.plot_surface(*self._surface, color=color, alpha=alpha)
