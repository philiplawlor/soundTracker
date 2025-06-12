import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:logger/logger.dart';

class WebSocketService {
  static const String _baseUrl = 'ws://localhost:8001';
  static const String _audioEndpoint = '/ws/audio';
  
  late WebSocketChannel _channel;
  final _logger = Logger();
  
  // Stream controllers for different types of messages
  final _statusController = StreamController<Map<String, dynamic>>.broadcast();
  final _devicesController = StreamController<List<dynamic>>.broadcast();
  final _audioLevelController = StreamController<Map<String, dynamic>>.broadcast();
  final _errorController = StreamController<String>.broadcast();
  
  // Public streams
  Stream<Map<String, dynamic>> get statusStream => _statusController.stream;
  Stream<List<dynamic>> get devicesStream => _devicesController.stream;
  Stream<Map<String, dynamic>> get audioLevelStream => _audioLevelController.stream;
  Stream<String> get errorStream => _errorController.stream;
  
  bool get isConnected => _channel != null && _channel.closeCode == null;
  
  Future<void> connect() async {
    try {
      final wsUrl = '$_baseUrl$_audioEndpoint';
      _logger.i('Connecting to WebSocket at $wsUrl');
      
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      
      _channel.stream.listen(
        (message) => _handleMessage(message),
        onError: (error) {
          _logger.e('WebSocket error: $error');
          _errorController.add('Connection error: $error');
        },
        onDone: () {
          _logger.w('WebSocket connection closed');
          _errorController.add('Connection closed');
        },
        cancelOnError: true,
      );
      
      _logger.i('WebSocket connected');
      
      // Request devices list after connection
      getDevices();
      
    } catch (e) {
      _logger.e('Failed to connect to WebSocket: $e');
      _errorController.add('Failed to connect: $e');
      rethrow;
    }
  }
  
  void disconnect() {
    _logger.i('Disconnecting WebSocket');
    _channel.sink.close();
    _statusController.close();
    _devicesController.close();
    _audioLevelController.close();
    _errorController.close();
  }
  
  void getDevices() {
    _sendMessage({'type': 'get_devices'});
  }
  
  void startAudioCapture(int deviceId) {
    _sendMessage({
      'type': 'start_capture',
      'device_id': deviceId,
    });
  }
  
  void stopAudioCapture() {
    _sendMessage({'type': 'stop_capture'});
  }
  
  void _sendMessage(Map<String, dynamic> message) {
    try {
      if (_channel.closeCode == null) {
        _channel.sink.add(jsonEncode(message));
        _logger.d('Sent message: $message');
      } else {
        _logger.w('Cannot send message, WebSocket is not connected');
        _errorController.add('Not connected to server');
      }
    } catch (e) {
      _logger.e('Error sending WebSocket message: $e');
      _errorController.add('Failed to send message: $e');
    }
  }
  
  void _handleMessage(dynamic message) {
    try {
      _logger.d('Received message: $message');
      
      final data = jsonDecode(message) as Map<String, dynamic>;
      final type = data['type'] as String?;
      
      if (type == null) {
        _logger.w('Received message without type: $message');
        return;
      }
      
      switch (type) {
        case 'status':
          _statusController.add(data);
          break;
          
        case 'devices':
          final devices = data['devices'] as List<dynamic>? ?? [];
          _devicesController.add(devices);
          break;
          
        case 'audio_level':
          _audioLevelController.add(data);
          break;
          
        case 'error':
          final errorMsg = data['message'] as String? ?? 'Unknown error';
          _errorController.add(errorMsg);
          break;
          
        default:
          _logger.w('Unknown message type: $type');
          break;
      }
    } catch (e) {
      _logger.e('Error handling WebSocket message: $e\nMessage: $message');
      _errorController.add('Error processing message: $e');
    }
  }
}
