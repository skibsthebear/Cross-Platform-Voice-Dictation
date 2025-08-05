#!/usr/bin/env python3
"""
Simple PyQt6 recording indicator that shows "Recording" text
"""

import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class RecordingIndicator(QWidget):
    def __init__(self, x=None, y=None):
        super().__init__()
        
        # Parse command line arguments for position
        if x is None and len(sys.argv) >= 3:
            try:
                x = int(sys.argv[1])
                y = int(sys.argv[2])
            except:
                x = 640
                y = 360
        
        # Default to center if not provided
        if x is None:
            x = 640
            y = 360
            
        self.init_ui(x, y)
        
    def init_ui(self, x, y):
        # Create label for text
        self.label = QLabel('🔴 Recording', self)
        
        # Set font - smaller size
        font = QFont('Arial', 10, QFont.Weight.Bold)
        self.label.setFont(font)
        
        # Style the label with white text and dark semi-transparent background
        self.label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(40, 40, 40, 200);
                padding: 5px 10px;
                border-radius: 4px;
            }
        """)
        
        # Adjust label size to content
        self.label.adjustSize()
        
        # Set window flags for borderless, always on top, transparent background
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Make window transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Position the window with offset from mouse
        self.move(x + 20, y + 20)
        
        # Resize window to fit label
        self.resize(self.label.size())
        
        # Animation timer for pulsing effect
        self.opacity = 1.0
        self.opacity_direction = -0.05
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)  # 20 FPS
        
    def animate(self):
        # Pulse the opacity
        self.opacity += self.opacity_direction
        if self.opacity <= 0.7:
            self.opacity = 0.7
            self.opacity_direction = 0.05
        elif self.opacity >= 1.0:
            self.opacity = 1.0
            self.opacity_direction = -0.05
            
        # Update window opacity
        self.setWindowOpacity(self.opacity)

def main():
    app = QApplication(sys.argv)
    
    # Create and show the indicator
    indicator = RecordingIndicator()
    indicator.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == '__main__':
    main()