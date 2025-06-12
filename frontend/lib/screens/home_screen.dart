import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:frontend/providers/audio_provider.dart';
import 'package:frontend/widgets/audio_level_indicator.dart';
import 'package:frontend/widgets/device_dropdown.dart';
import 'package:frontend/widgets/connection_status.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with SingleTickerProviderStateMixin {
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _initializeAudio();
  }

  Future<void> _initializeAudio() async {
    try {
      final audioProvider = context.read<AudioProvider>();
      
      // Listen for connection status changes
      audioProvider.addListener(() {
        if (mounted) {
          setState(() {
            _isLoading = false;
            _errorMessage = audioProvider.connectionError;
          });
        }
      });
      
      // Initial connection
      await audioProvider.connect();
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _errorMessage = 'Failed to initialize audio: $e';
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SoundTracker'),
        actions: const [
          ConnectionStatus(),
          SizedBox(width: 16),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_errorMessage != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 48, color: Colors.red),
              const SizedBox(height: 16),
              Text(
                'Error: $_errorMessage',
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.red),
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: _initializeAudio,
                icon: const Icon(Icons.refresh),
                label: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Device selection
          const Text('Select Audio Device:', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          const DeviceDropdown(),
          const SizedBox(height: 32),
          
          // Audio level visualization
          const Text('Audio Level:', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          const AudioLevelIndicator(),
          const SizedBox(height: 32),
          
          // Controls
          Consumer<AudioProvider>(
            builder: (context, audioProvider, _) {
              final isCapturing = audioProvider.currentStatus?['is_capturing'] == true;
              
              return ElevatedButton.icon(
                onPressed: () {
                  if (isCapturing) {
                    audioProvider.stopCapture();
                  } else {
                    // Get the first available device if none is selected
                    final deviceId = audioProvider.devices.isNotEmpty 
                        ? audioProvider.devices[0]['id'] 
                        : null;
                    if (deviceId != null) {
                      audioProvider.startCapture(deviceId);
                    }
                  }
                },
                icon: Icon(isCapturing ? Icons.stop : Icons.mic),
                label: Text(isCapturing ? 'Stop Capture' : 'Start Capture'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  backgroundColor: isCapturing ? Colors.red : Theme.of(context).primaryColor,
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    super.dispose();
  }
}
