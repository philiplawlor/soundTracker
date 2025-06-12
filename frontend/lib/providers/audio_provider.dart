import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:provider/provider.dart';
import '../services/websocket_service.dart';

class AudioProvider with ChangeNotifier {
  final WebSocketService _webSocketService;
  
  // Connection state
  bool _isConnected = false;
  String? _connectionError;
  
  // Audio data
  List<dynamic> _devices = [];
  Map<String, dynamic>? _currentStatus;
  double _audioLevel = 0.0;
  double _dbLevel = -100.0;
  
  // Getters
  bool get isConnected => _isConnected;
  String? get connectionError => _connectionError;
  List<dynamic> get devices => _devices;
  Map<String, dynamic>? get currentStatus => _currentStatus;
  double get audioLevel => _audioLevel;
  double get dbLevel => _dbLevel;
  
  AudioProvider(this._webSocketService) {
    _setupWebSocketListeners();
  }
  
  void _setupWebSocketListeners() {
    // Listen for connection status updates
    _webSocketService.statusStream.listen((status) {
      _currentStatus = status;
      _isConnected = true;
      _connectionError = null;
      notifyListeners();
    });
    
    // Listen for device list updates
    _webSocketService.devicesStream.listen((devices) {
      _devices = devices;
      notifyListeners();
    });
    
    // Listen for audio level updates
    _webSocketService.audioLevelStream.listen((data) {
      _audioLevel = (data['rms'] ?? 0.0).toDouble();
      _dbLevel = (data['db'] ?? -100.0).toDouble();
      notifyListeners();
    });
    
    // Listen for errors
    _webSocketService.errorStream.listen((error) {
      _connectionError = error;
      _isConnected = false;
      notifyListeners();
    });
  }
  
  Future<void> connect() async {
    try {
      await _webSocketService.connect();
      _isConnected = true;
      _connectionError = null;
      notifyListeners();
    } catch (e) {
      _isConnected = false;
      _connectionError = 'Failed to connect: $e';
      notifyListeners();
      rethrow;
    }
  }
  
  void disconnect() {
    _webSocketService.disconnect();
    _isConnected = false;
    notifyListeners();
  }
  
  void refreshDevices() {
    _webSocketService.getDevices();
  }
  
  void startCapture(int deviceId) {
    _webSocketService.startAudioCapture(deviceId);
  }
  
  void stopCapture() {
    _webSocketService.stopAudioCapture();
  }
  
  @override
  void dispose() {
    _webSocketService.disconnect();
    super.dispose();
  }
}

// Helper extension to easily access the provider
extension AudioProviderExtension on BuildContext {
  AudioProvider get audioProvider => Provider.of<AudioProvider>(this, listen: false);
  AudioProvider get watchAudioProvider => Provider.of<AudioProvider>(this);
}
