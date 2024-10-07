# Proxy Checker

Welcome to the Proxy Checker documentation!

Proxy Checker is a simple desktop application designed to verify and analyze proxy servers. Built with Python and PyQt6, this tool helps users quickly assess the quality and reliability of HTTP and SOCKS5 proxies.

## Features

- **Multi-Protocol Support**: Check both HTTP and SOCKS5 proxies.
- **Fraud Score Analysis**: Utilizes IPQualityScore API to evaluate proxy reliability.
- **Bulk Checking**: Test multiple proxies simultaneously.
- **User-Friendly GUI**: Easy-to-use interface built with PyQt6.
- **Detailed Results**: Get comprehensive information about each proxy, including location and ISP details.
- **Export Functionality**: Save results to a CSV file for further analysis.

## Getting the Application

You have two options to get Proxy Checker:

1. **Download Compiled Version (Windows and MacOS Intel-based)**:
   - Visit our [GitHub Releases](https://github.com/Neverlow512/ProxyChecker/releases) page.
   - Download the latest version for your operating system:
     - Windows: `ProxyChecker-Windows(Release)`
     - MacOS (Intel-based): `ProxyChecker-MacOS-Intel(Release Intel)`
   - Note: A compiled version for Silicon-based Macs is not currently available.

2. **Use Uncompiled Source Code (All platforms, including Silicon-based Macs)**:
   - Clone the repository: `git clone https://github.com/Neverlow512/ProxyChecker.git`
   - Follow the platform-specific instructions below to install dependencies and run the application.

## Installation and Running

### For Compiled Versions:
1. Download the appropriate ZIP file for your system from the Releases page.
2. Extract the ZIP file to your preferred location.
3. Run `ProxyChecker.exe` (Windows) or `ProxyChecker.app` (MacOS) to start the application.

### For Uncompiled Source Code:

#### Windows:
1. Install Python 3.7 or later from [python.org](https://www.python.org/downloads/).
2. Open Command Prompt and navigate to the project directory.
3. Install required packages:
   ```
   pip install PyQt6 requests pyinstaller
   ```
4. Run the application:
   ```
   python proxy_checker_gui.py
   ```
5. (Optional) To compile into an executable:
   ```
   pyinstaller proxy_checker.spec
   ```

#### macOS (Intel and Silicon):
1. Install Python 3.7 or later from [python.org](https://www.python.org/downloads/).
2. Open Terminal and navigate to the project directory.
3. Install required packages:
   ```
   pip3 install PyQt6 requests pyinstaller
   ```
4. Run the application:
   ```
   python3 proxy_checker_gui.py
   ```
5. (Optional) To compile into an application bundle:
   ```
   pyinstaller proxy_checker.spec
   ```

#### Linux:
1. Install Python 3.7 or later using your distribution's package manager.
2. Open a terminal and navigate to the project directory.
3. Install required packages:
   ```
   pip3 install PyQt6 requests pyinstaller
   ```
4. Run the application:
   ```
   python3 proxy_checker_gui.py
   ```
5. (Optional) To compile into an executable:
   ```
   pyinstaller proxy_checker.spec
   ```

Note: Ensure you have the necessary development tools installed on your system. For Linux, you may need to install `python3-dev` and `qt6-dev-tools` packages.

After compilation (if chosen), the executable or application bundle will be available in the `dist` folder.

## Usage Guide

1. **Launch the Application**: Double-click on `ProxyChecker.exe` (Windows) or `ProxyChecker.app` (MacOS).

2. **Enter API Key**: Input your IPQualityScore API key in the designated field. If you don't have an API key, you can obtain one from [IPQualityScore](https://www.ipqualityscore.com/).

3. **Select Proxy Type**: Choose between HTTP or SOCKS5 from the dropdown menu.

4. **Set Max Score**: Enter the maximum acceptable fraud score. Proxies with a fraud score below this value will be considered valid.

5. **Input Proxies**: Enter your list of proxies in the text area, one per line, using the following format:
   - For proxies without authentication: `ip:port`
   - For proxies with authentication: `ip:port:username:password`

6. **Start Checking**: Click the "Check Proxies" button to begin the verification process.

7. **Monitor Progress**: The progress bar will display the checking progress, and the log area will show results for each proxy.

8. **View Results**: Once completed, a CSV file named `proxy_results.csv` will be created in the application directory with detailed results.

## Troubleshooting

- Ensure all files from the ZIP archive are in the same directory.
- If your antivirus flags the application, you may need to add an exception.
- For any issues, try running the application as an administrator.
- For Windows users, make sure you have the Microsoft Visual C++ Redistributable for Visual Studio 2015-2022 installed.

## Support

For updates and support, follow me on:
- [X.com](https://x.com/traffic_goat)
- [Reddit.com](https://www.reddit.com/user/Neverlow512/)

## Legal

This tool is for educational and legitimate testing purposes only. Ensure you have the right to check the proxies you're testing. The developer is not responsible for any misuse of this tool.

## Contributing

While this is a personal project, I welcome contributions! If you'd like to contribute, please check out the [GitHub repository](https://github.com/Neverlow512/ProxyChecker) and submit a pull request.
