from manim import *

class MovingCameraExample(MovingCameraScene):
    def construct(self):
        # Create a circle
        circle = Circle()
        self.play(Create(circle))

        # Zoom in on the circle using the camera frame
        self.play(self.camera.frame.animate.scale(0.5).move_to(circle.get_center()))

        # Wait for a while before finishing the scene
        self.wait(2)
