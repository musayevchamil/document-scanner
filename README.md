# Document Scanner Application

## Overview
The Document Scanner is a Python-based GUI application designed for efficient and user-friendly document scanning. It allows users to digitize physical documents by processing images, offering features like edge detection, manual corner adjustment, and perspective correction.

## Features
- **Interactive Image Selection:** Easily browse and select document images.
- **Automatic Document Edge Detection:** Detects document edges within the image automatically.
- **Manual Corner Adjustment:** Manually fine-tune the corners of the detected document for precise alignment.
- **Perspective Correction:** Transforms the document to a flat perspective, suitable for digital storage or printing.
- **Real-Time Display:** Immediate visual feedback as adjustments are made.
- **Save Functionality:** Save the processed document in various file formats.

## Usage
1. **Launch Application:** Run the Document Scanner application.
2. **Select Image:** Use the 'Browse' button to choose an image file containing the document.
3. **Automatic and Manual Adjustments:** The application will initially detect document edges, which can then be manually adjusted.
4. **Apply Perspective Transformation:** Adjust the document's perspective to achieve a flat, readable view.
5. **Save Processed Image:** After processing, save the final image by clicking the 'Save' button and selecting the desired format and location.

## Requirements
- Python 3.x
- tkinter for the GUI interface
- OpenCV (cv2) for image processing
- PIL (Pillow) for additional image handling
- NumPy for numerical operations

To install the necessary Python libraries:
```bash
pip install opencv-python pillow numpy
```

## Contributions
Contributions to the Document Scanner application are highly encouraged. Feel free to fork the repository, implement your changes, and submit pull requests for any enhancements or bug fixes.

## License
The Document Scanner application is open-source, distributed under the MIT License. For more information, please refer to the [LICENSE](LICENSE) file in the repository.
