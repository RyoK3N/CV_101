import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Slider, Button

class Camera:
    def __init__(self, position=np.array([2, -4, 2]), up=np.array([0, 0, 1]), size=0.3):
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
        self._direction = target - self.position
        self._direction = self._direction / np.linalg.norm(self._direction)
        self._update_camera()
    
    def _update_camera(self):
        if self._direction is None:
            return
            
        self._right = np.cross(self._direction, self._up)
        self._right = self._right / np.linalg.norm(self._right)
        self._up = np.cross(self._right, self._direction)
        self._up = self._up / np.linalg.norm(self._up)
        
        self._update_vertices()
    
    def _update_vertices(self):
        self._vertices = np.array([
            self.position,
            self.position + self.size * (-self._right + self._direction - self._up),
            self.position + self.size * (self._right + self._direction - self._up),
            self.position + self.size * (self._right + self._direction + self._up),
            self.position + self.size * (-self._right + self._direction + self._up)
        ])

class Cube:
    def __init__(self, origin=np.array([0, 0, 0]), size=1):
        self._origin = np.array(origin)
        self._size = size
        self._vertices = None
        self._edges = None
        self._update_geometry()
    
    @property
    def center(self):
        return self._origin + self._size/2
    
    def _update_geometry(self):
        o = self._origin
        s = self._size
        
        self._vertices = np.array([
            o + [0,0,0], o + [s,0,0], o + [0,s,0], o + [s,s,0],
            o + [0,0,s], o + [s,0,s], o + [0,s,s], o + [s,s,s]
        ])
        
        edge_indices = [
            (0,1), (0,2), (0,4), (1,3), (1,5), (2,3),
            (2,6), (4,5), (4,6), (7,3), (7,5), (7,6)
        ]
        
        self._edges = []
        for start_idx, end_idx in edge_indices:
            self._edges.append([
                self._vertices[start_idx],
                self._vertices[end_idx]
            ])

class Scene3DViewer:
    def __init__(self):
        # Create figure with two subplots side by side
        self.fig = plt.figure(figsize=(15, 8))
        
        # Add 3D subplot for scene
        self.ax = self.fig.add_subplot(121, projection='3d')
        
        # Add 2D subplot for projected view
        self.ax2 = self.fig.add_subplot(122)
        
        # Initialize objects
        self.camera = Camera()
        self.cube = Cube()
        
        # Set camera to look at cube
        self.camera.look_at(self.cube.center)
        
        # Add sliders
        self.setup_sliders()
        
        # Set up the plot
        self.setup_plot()
        
    def setup_sliders(self):
        # Add slider axes
        slider_color = 'lightgoldenrodyellow'
        slider_height = 0.02
        slider_width = 0.3
        
        # Camera position sliders
        ax_x = plt.axes([0.15, 0.02, slider_width, slider_height], facecolor=slider_color)
        ax_y = plt.axes([0.15, 0.05, slider_width, slider_height], facecolor=slider_color)
        ax_z = plt.axes([0.15, 0.08, slider_width, slider_height], facecolor=slider_color)
        
        self.slider_x = Slider(ax_x, 'Camera X', -5.0, 5.0, valinit=2.0)
        self.slider_y = Slider(ax_y, 'Camera Y', -5.0, 5.0, valinit=-4.0)
        self.slider_z = Slider(ax_z, 'Camera Z', -5.0, 5.0, valinit=2.0)
        
        # View angle sliders
        ax_elev = plt.axes([0.6, 0.02, slider_width, slider_height], facecolor=slider_color)
        ax_azim = plt.axes([0.6, 0.05, slider_width, slider_height], facecolor=slider_color)
        
        self.slider_elev = Slider(ax_elev, 'Elevation', -90, 90, valinit=20)
        self.slider_azim = Slider(ax_azim, 'Azimuth', 0, 360, valinit=45)
        
        # Update function for sliders
        def update(val):
            self.camera.position = np.array([
                self.slider_x.val,
                self.slider_y.val,
                self.slider_z.val
            ])
            self.camera.look_at(self.cube.center)
            self.ax.view_init(elev=self.slider_elev.val, azim=self.slider_azim.val)
            self.setup_plot()
            self.fig.canvas.draw_idle()
        
        # Register update function with sliders
        self.slider_x.on_changed(update)
        self.slider_y.on_changed(update)
        self.slider_z.on_changed(update)
        self.slider_elev.on_changed(update)
        self.slider_azim.on_changed(update)
        
    def setup_plot(self):
        # Clear both axes
        self.ax.cla()
        self.ax2.cla()
        
        # Draw in 3D subplot
        self.draw_cube()
        self.draw_camera()
        
        # Set labels and title for 3D plot
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_title('3D Scene')
        
        # Set view limits
        scale = 5
        self.ax.set_xlim(-scale, scale)
        self.ax.set_ylim(-scale, scale)
        self.ax.set_zlim(-scale, scale)
        
        # Draw in 2D subplot (projected view)
        self.draw_projected_view()
        
        # Set labels and title for 2D plot
        self.ax2.set_xlabel('x')
        self.ax2.set_ylabel('y')
        self.ax2.set_title('Camera View (2D Projection)')
        self.ax2.grid(True)
        
    def draw_camera(self):
        vertices = self.camera._vertices
        if vertices is not None:
            # Draw edges from apex to base
            for i in range(1, 5):
                self.ax.plot([vertices[0][0], vertices[i][0]],
                           [vertices[0][1], vertices[i][1]],
                           [vertices[0][2], vertices[i][2]],
                           'g-', linewidth=2)
            
            # Draw base
            base_indices = [1, 2, 3, 4, 1]
            x = [vertices[i][0] for i in base_indices]
            y = [vertices[i][1] for i in base_indices]
            z = [vertices[i][2] for i in base_indices]
            self.ax.plot(x, y, z, 'g-', linewidth=2)
            
            # Draw camera position
            self.ax.scatter([vertices[0][0]], [vertices[0][1]], [vertices[0][2]],
                          color='g', s=100)
    
    def draw_cube(self):
        vertices = self.cube._vertices
        edges = self.cube._edges
        
        # Draw vertices
        self.ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2],
                       color='b', s=50)
        
        # Draw edges
        for edge in edges:
            start, end = edge
            self.ax.plot([start[0], end[0]],
                        [start[1], end[1]],
                        [start[2], end[2]],
                        'r-', linewidth=2)
    
    def draw_projected_view(self):
        # Define camera parameters for projection
        camera_matrix = np.array([
            [800., 0., 320.],
            [0., 800., 240.],
            [0., 0., 1.]
        ])
        
        # Get camera parameters
        camera_right = self.camera._right
        camera_up = self.camera._up
        camera_dir = self.camera._direction
        
        # Create rotation matrix from camera orientation
        rotation_matrix = np.column_stack([camera_right, np.cross(camera_up, camera_right), camera_up])
        translation_vector = -rotation_matrix @ self.camera.position
        
        # Project cube vertices
        vertices = self.cube._vertices
        projected_points = []
        for vertex in vertices:
            # Apply camera transform
            transformed = rotation_matrix @ vertex + translation_vector
            
            # Project to 2D (using homogeneous coordinates)
            z = transformed[2]
            if z < 0.1:  # Avoid division by very small numbers
                z = 0.1
            x = transformed[0] / z
            y = transformed[1] / z
            
            # Apply camera matrix
            projected = camera_matrix @ np.array([x, y, 1.0])
            projected_points.append(projected[:2])  # Only keep x, y coordinates
        
        projected_points = np.array(projected_points)
        
        # Set reasonable view limits for 2D projection
        self.ax2.set_xlim(0, 640)  # Image width
        self.ax2.set_ylim(480, 0)  # Image height (inverted for standard image coordinates)
        
        # Draw projected points
        self.ax2.scatter(projected_points[:, 0], projected_points[:, 1], c='b')
        
        # Draw projected edges
        for edge in self.cube._edges:
            start_idx = np.where(np.all(vertices == edge[0], axis=1))[0][0]
            end_idx = np.where(np.all(vertices == edge[1], axis=1))[0][0]
            self.ax2.plot([projected_points[start_idx, 0], projected_points[end_idx, 0]],
                         [projected_points[start_idx, 1], projected_points[end_idx, 1]], 'r-')

def main():
    viewer = Scene3DViewer()
    plt.show()

if __name__ == '__main__':
    main()

