# Lux Mobile Client

A lightweight Flutter client for browsing the **Lux** puzzle catalog. It communicates with the Lux server's versioned REST API (`GET /api/v1/levels`) to display puzzle metadata, complete with loading states, graceful error recovery, search, and category filtering.

---

## Features

- **Puzzle Catalog**: Lists all available puzzle levels with category badges, difficulty indicators (Easy, Medium, Hard, Expert), and tags.
- **Puzzle Details**: Tap any level to open a bottom sheet with detailed description, hints, validator information, and full tags.
- **Search & Filtering**: Real-time search query matching across titles, descriptions, IDs, and tags, as well as category filtering.
- **Robust Error Handling**: Actionable connection error messages and retry flows if the server is unreachable.
- **Configurable Server URL**: Configure the Lux base URL via `--dart-define` or directly in-app using the server settings dialog (with presets for Android emulator `http://10.0.2.2:5050` and localhost `http://127.0.0.1:5050`).
- **Clean Architecture & Full Test Coverage**: Unit tests for models, API service, and widget test coverage for all UI states.

---

## Prerequisites

- [Flutter SDK](https://docs.flutter.dev/get-started/install) (`^3.47.0` or newer)
- [Dart SDK](https://dart.dev/get-dart) (`^3.13.0` or newer)
- Python 3.9+ (to run the local Lux server)

---

## Getting Started

### 1. Start the Lux Server

From the root of the `lux` repository:

```bash
# Install server dependencies if needed
pip install -r requirements.txt

# Start the Lux server (runs on http://127.0.0.1:5050 by default)
python server.py
```

Verify that the server is running by opening `http://127.0.0.1:5050/api/v1/levels` in your browser.

---

### 2. Configure the Base URL

The default base URL is `http://127.0.0.1:5050`. Depending on your environment:

| Target Platform / Device | Recommended Base URL |
| :--- | :--- |
| **Desktop (macOS / Windows / Linux)** | `http://127.0.0.1:5050` |
| **Web Browser** | `http://127.0.0.1:5050` |
| **iOS Simulator** | `http://127.0.0.1:5050` |
| **Android Emulator** | `http://10.0.2.2:5050` |
| **Physical Device (WiFi)** | `http://<your-computer-local-ip>:5050` |

#### Option A: In-App Configuration (Recommended)
Tap the **Server Settings** (`dns`) icon in the app bar or click **Server Settings** on the error screen to change the base URL or select a preset anytime.

#### Option B: Build-time / Run-time Flag
Pass `--dart-define=LUX_BASE_URL=<url>` when running or building the app:

```bash
flutter run --dart-define=LUX_BASE_URL=http://10.0.2.2:5050
```

---

### 3. Run the App

From the `mobile/` directory:

```bash
# Get dependencies
flutter pub get

# Run on connected device or emulator
flutter run
```

---

### 4. Run Tests

To execute all unit and widget tests:

```bash
flutter test
```

---

## Project Structure

```text
mobile/
├── lib/
│   ├── main.dart                      # App entry point and theme setup
│   ├── models/
│   │   └── level.dart                 # Level model, JSON parsing & serialization
│   ├── screens/
│   │   └── catalog_screen.dart        # Main catalog UI with search & category filters
│   ├── services/
│   │   └── lux_api_service.dart       # HTTP client and custom exceptions
│   └── widgets/
│       ├── level_card.dart            # Puzzle card and detail modal sheet
│       ├── server_config_dialog.dart  # In-app server URL configuration dialog
│       └── state_views.dart           # Loading, Error, and Empty state views
├── test/
│   ├── models/
│   │   └── level_test.dart            # Level model parsing and equality tests
│   ├── screens/
│   │   └── catalog_screen_test.dart   # Catalog UI state & interaction widget tests
│   ├── services/
│   │   └── lux_api_service_test.dart  # API service mock client tests
│   └── widget_test.dart               # App smoke test
├── pubspec.yaml                       # Flutter dependencies & metadata
└── README.md                          # Mobile client documentation
```
