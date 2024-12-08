# from manim import *


# class CreateCircle(Scene):
#     def construct(self):
#         circle = Circle()  # create a circle
#         circle.set_fill(PINK, opacity=0.5)  # set the color and transparency
#         self.play(Create(circle))  # show the circle on screen

from manim import *

class Lock(VGroup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create the body of the lock (circle)
        body = Circle(radius=0.5, color=WHITE)
        # Create the key part of the lock (line)
        key = Line(start=body.get_top(), end=body.get_bottom(), color=WHITE)
        key.move_to(body.get_center())

        # Add the components to the Lock
        self.add(body, key)



class Cloud(VGroup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create several circles to form the shape of the cloud
        cloud_parts = [
            Circle(radius=0.6, color=WHITE).shift(LEFT),
            Circle(radius=0.5, color=WHITE).shift(RIGHT),
            Circle(radius=0.7, color=WHITE).shift(DOWN),
            Circle(radius=0.5, color=WHITE).shift(UP),
        ]
        # Combine all the parts to form the cloud
        self.add(*cloud_parts)



# Lock class
class Lock(VGroup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create the body of the lock (circle)
        body = Circle(radius=0.5, color=WHITE)
        # Create the key part of the lock (line)
        key = Line(start=body.get_top(), end=body.get_bottom(), color=WHITE)
        key.move_to(body.get_center())
        # Add the components to the Lock
        self.add(body, key)

# Cloud class
class Cloud(VGroup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create several circles to form the shape of the cloud
        cloud_parts = [
            Circle(radius=0.6, color=WHITE).shift(LEFT),
            Circle(radius=0.5, color=WHITE).shift(RIGHT),
            Circle(radius=0.7, color=WHITE).shift(DOWN),
            Circle(radius=0.5, color=WHITE).shift(UP),
        ]
        # Combine all the parts to form the cloud
        self.add(*cloud_parts)

class ProjectFlowScene(Scene):
    def construct(self):
        # Scene 1: Introduction
        title = Text("IoT Data Flow Project Overview").scale(1.5)
        description = Text("From IoT sensors -> Kafka -> Spark -> 5G -> Decoding -> Visualization & AI").next_to(title, DOWN)
        self.play(Write(title))
        self.play(Write(description))
        self.wait(1)
        self.clear()

        # Scene 2: Data Extraction from IoT Sensors
        sensor_text = Text("IoT Sensors capturing data").scale(1.2)
        sensor_image = Circle().set_color(PINK).scale(0.5)
        self.play(Write(sensor_text))
        self.play(Create(sensor_image))
        self.wait(1)
        self.clear()

        # Scene 3: Kafka and Spark
        kafka_text = Text("Data streaming through Kafka").shift(UP)
        spark_text = Text("Data processing with Spark").shift(DOWN)
        kafka_box = Rectangle(width=2, height=1).set_color(WHITE)
        kafka_arrow = Arrow(start=LEFT, end=RIGHT).shift(UP)
        spark_box = Rectangle(width=2, height=1).set_color(WHITE).shift(DOWN)
        
        self.play(Write(kafka_text), Create(kafka_box))
        self.play(Write(spark_text), Create(spark_box), Create(kafka_arrow))
        self.wait(1)
        self.clear()

        # Scene 4: 5G Transmission
        transmission_text = Text("Data transmitted via 5G").shift(UP)
        cloud = Cloud().shift(DOWN)
        self.play(Write(transmission_text), Create(cloud))
        self.wait(1)
        self.clear()

        # Scene 5: Data Decryption
        lock = Lock().shift(LEFT)
        unlock = Lock().shift(RIGHT)  # Using Lock here to represent the unlocking process
        decrypt_text = Text("Decryption of Data").shift(UP)
        self.play(Write(decrypt_text), Create(lock), Create(unlock))
        self.wait(1)
        self.clear()

        # Scene 6: Visualization & AI Analysis
        graph_text = Text("Data Visualization in Grafana").shift(UP)
        ai_text = Text("AI Analyzes for Insights").shift(DOWN)
        self.play(Write(graph_text))
        self.play(Write(ai_text))
        self.wait(1)
        self.clear()

        # Scene 7: Conclusion
        conclusion_text = Text("Predictive Maintenance and Real-time Decision Making").scale(1.2)
        self.play(Write(conclusion_text))
        self.wait(2)
