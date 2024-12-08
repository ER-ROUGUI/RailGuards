from manim import *


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


class ProjectIntro(Scene):
    def construct(self):
        title = Text("IoT Data Flow for TGV Train Project").scale(1.5)
        description = Text("From Sensors to Real-time Analytics and AI").next_to(title, DOWN)
        self.play(Write(title))
        self.play(Write(description))
        self.wait(2)
        self.clear()


class TGVTrainScene(Scene):
    def construct(self):
        tgv_train = ImageMobject("tgv.jpg").scale(0.5)  # Replace with actual image path
        self.play(FadeIn(tgv_train))
        self.wait(1)
        
        # Scale the image and position it in the top-left corner
        self.play(tgv_train.animate.scale(0.3).to_corner(UP + LEFT))
        self.wait(1)


class IoTSensorsScene(MovingCameraScene):
    def construct(self):
        tgv_train = ImageMobject("vibration.jpg").scale(0.5)  # Replace with actual image path
        self.play(FadeIn(tgv_train))
        self.wait(1)
        
        # Adding circles to represent IoT sensors
        sensor_positions = [UP + LEFT, DOWN + LEFT, RIGHT]
        sensors = VGroup()
        
        for position in sensor_positions:
            sensor = Circle(radius=0.1, color=BLUE).shift(position)
            sensors.add(sensor)
        
        self.play(FadeIn(sensors))
        
        # Zoom effect to focus on the IoT sensors
        self.play(self.camera.frame.animate.scale(0.6).move_to(sensors.get_center()))
        self.wait(1)
        self.clear()


class ServerAndProcessingScene(Scene):
    def construct(self):
        # Create local server box
        server_box = Rectangle(width=3, height=1, color=WHITE)
        server_text = Text("Local Server").next_to(server_box, DOWN)
        self.play(Create(server_box), Write(server_text))
        self.wait(1)

        # Show Kafka & Spark (can use simple box shapes with text)
        kafka_box = Rectangle(width=2, height=1, color=WHITE).shift(RIGHT * 4)
        kafka_text = Text("Kafka").next_to(kafka_box, DOWN)
        spark_box = Rectangle(width=2, height=1, color=WHITE).shift(RIGHT * 6)
        spark_text = Text("Spark").next_to(spark_box, DOWN)
        
        self.play(Create(kafka_box), Write(kafka_text))
        self.wait(1)
        self.play(Create(spark_box), Write(spark_text))
        self.wait(1)
        
        # Draw arrows from the server to Kafka and Spark
        arrow_to_kafka = Arrow(server_box.get_right(), kafka_box.get_left())
        arrow_to_spark = Arrow(kafka_box.get_right(), spark_box.get_left())
        self.play(Create(arrow_to_kafka), Create(arrow_to_spark))
        self.wait(1)


class EncryptionScene(Scene):
    def construct(self):
        encryption_text = Text("Encrypting Data").scale(1.2).shift(UP)
        self.play(Write(encryption_text))
        self.wait(1)
        
        # Show binary symbols to indicate encryption
        binary_code = Text("01010101", color=YELLOW).shift(DOWN)
        self.play(Write(binary_code))
        self.wait(1)
        self.clear()


class TransmissionScene(Scene):
    def construct(self):
        transmission_text = Text("Transmitting Data via 5G").scale(1.2).shift(UP)
        self.play(Write(transmission_text))
        
        # Draw a 5G cloud symbol
        cloud = Cloud().shift(DOWN)
        self.play(Create(cloud))
        self.wait(1)
        self.clear()


class DataCaptureScene(Scene):
    def construct(self):
        station_text = Text("Main Station: SIANA").scale(1.2).shift(UP)
        self.play(Write(station_text))
        
        # Create a SIANA station
        station = Rectangle(width=3, height=1, color=WHITE).shift(DOWN)
        self.play(Create(station))
        self.wait(1)
        self.clear()


class DecryptionAndAI(Scene):
    def construct(self):
        decryption_text = Text("Decrypting Data").scale(1.2).shift(UP)
        self.play(Write(decryption_text))
        
        # Show decrypted data (e.g., temperature, vibration values)
        decrypted_data = Text("Temperature: 25°C | Vibration: 1.5 m/s²").shift(DOWN)
        self.play(Write(decrypted_data))
        
        # Show AI model usage
        ai_text = Text("AI Model Processing").shift(DOWN * 2)
        self.play(Write(ai_text))
        self.wait(1)
        self.clear()


class ConclusionScene(Scene):
    def construct(self):
        conclusion_text = Text("Final Dashboard & Insights").scale(1.5)
        self.play(Write(conclusion_text))
        self.wait(2)
        self.clear()


class FullProjectFlow(MovingCamera):
    def construct(self):
        # Project Intro
        self.play(Write(Text("IoT Data Flow for TGV Train Project").scale(1.5)))
        title = Text("TGV").scale(1.5)
        self.play(Write(Text("From Sensors to Real-time Analytics and AI").next_to(title, DOWN)))
        self.wait(2)
        self.clear()

        # TGV Train
        tgv_train = ImageMobject("tgv.jpg").scale(0.5)  # Replace with actual image path
        self.play(FadeIn(tgv_train))
        self.wait(1)
        self.play(tgv_train.animate.scale(0.3).to_corner(UP + LEFT))
        self.wait(1)
        self.clear()

        # IoT Sensors
        sensor_positions = [UP + LEFT, DOWN + LEFT, RIGHT]
        sensors = VGroup()
        for position in sensor_positions:
            sensor = Circle(radius=0.1, color=BLUE).shift(position)
            sensors.add(sensor)
        self.play(FadeIn(sensors))
        # self.play(self.camera.frame.animate.scale(0.6).move_to(sensors.get_center()))
        self.wait(1)
        self.clear()

        # Server and Processing with Arrows
        server_box = Rectangle(width=3, height=1, color=WHITE)
        server_text = Text("Local Server").next_to(server_box, DOWN)
        self.play(Create(server_box), Write(server_text))
        self.wait(1)

        kafka_box = Rectangle(width=2, height=1, color=WHITE).shift(RIGHT * 4)
        kafka_text = Text("Kafka").next_to(kafka_box, DOWN)
        spark_box = Rectangle(width=2, height=1, color=WHITE).shift(RIGHT * 6)
        spark_text = Text("Spark").next_to(spark_box, DOWN)
        self.play(Create(kafka_box), Write(kafka_text))
        self.wait(1)
        self.play(Create(spark_box), Write(spark_text))
        self.wait(1)

        # Add Arrows
        arrow_to_kafka = Arrow(server_box.get_right(), kafka_box.get_left())
        arrow_to_spark = Arrow(kafka_box.get_right(), spark_box.get_left())
        self.play(Create(arrow_to_kafka), Create(arrow_to_spark))
        self.wait(1)
        self.clear()

        # Encryption
        encryption_text = Text("Encrypting Data").scale(1.2).shift(UP)
        self.play(Write(encryption_text))
        self.wait(1)
        binary_code = Text("01010101", color=YELLOW).shift(DOWN)
        self.play(Write(binary_code))
        self.wait(1)
        self.clear()

        # 5G Transmission
        transmission_text = Text("Transmitting Data via 5G").scale(1.2).shift(UP)
        self.play(Write(transmission_text))

        cloud = Cloud().shift(DOWN)
        self.play(Create(cloud))
        self.wait(1)
        self.clear()

        # Data Capture in SIANA
        station_text = Text("Main Station: SIANA").scale(1.2).shift(UP)
        self.play(Write(station_text))
        station = Rectangle(width=3, height=1, color=WHITE).shift(DOWN)
        self.play(Create(station))
        self.wait(1)
        self.clear()

        # Decryption and AI model processing
        decryption_text = Text("Decrypting Data").scale(1.2).shift(UP)
        self.play(Write(decryption_text))
        decrypted_data = Text("Temperature: 25°C | Vibration: 1.5 m/s²").shift(DOWN)
        self.play(Write(decrypted_data))
        ai_text = Text("AI Model Processing").shift(DOWN * 2)
        self.play(Write(ai_text))
        self.wait(1)
        self.clear()

        # Final Dashboard
        conclusion_text = Text("Final Dashboard & Insights").scale(1.5)
        self.play(Write(conclusion_text))
        self.wait(2)
        self.clear()