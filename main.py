from gui.gui import CatiaGUI
from PyQt5.QtWidgets import QApplication
import sys
from assistant.assistant import CatiaAssistant  # ✅ Import Assistant (which uses LLM)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # ✅ Initialize Assistant (which now contains CatiaLLM)
    assistant = CatiaAssistant()
    
    # ✅ Pass the Assistant to the GUI
    window = CatiaGUI(assistant=assistant)
    
    window.show()
    sys.exit(app.exec_())
