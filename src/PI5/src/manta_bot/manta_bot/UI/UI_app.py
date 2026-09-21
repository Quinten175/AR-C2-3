import tkinter as tk
import threading
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool


class ROSNode(Node):
    def __init__(self):
        super().__init__('UI_app')
        self.pub = self.create_publisher(Bool, 'activate_mapping', 10)
        self.count = 0

    def toggle_mapping_state(self, state):
        msg = Bool()
        msg.data = state
        self.pub.publish(msg)


class App:
    def __init__(self):
        self.node = ROSNode()
        self.root = tk.Tk()
        self.root.title("UI Active Mapping")
        self.root.geometry("300x150")
        self.active_mapping_state = False

        self.btn = tk.Button(self.root, text="Toggle mapping",
                             width=10, command=self.toggle)
        self.btn.pack(pady=10)

        threading.Thread(target=self._spin, daemon=True).start()

    def _spin(self):
        rclpy.spin(self.node)
        self.node.destroy_node()

    def toggle(self):
        self.active_mapping_state = not self.active_mapping_state
        self.node.toggle_mapping_state(self.active_mapping_state)

    def run(self):
        self.root.mainloop()
        rclpy.shutdown()


def main():
    rclpy.init()
    app = App()
    app.run()


if __name__ == '__main__':
    main()   