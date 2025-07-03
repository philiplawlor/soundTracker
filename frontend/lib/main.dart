import 'dart:async';
import 'dart:io';
import 'dart:typed_data';
import 'dart:convert';
import 'dart:html' as html;
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:file_picker/file_picker.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;

void main() {
  runApp(const SoundTrackerApp());
}

/// Main app widget for SoundTracker frontend.
class SoundTrackerApp extends StatelessWidget {
  const SoundTrackerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SoundTracker',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const SoundIdentifyScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

/// Main screen: pick/record audio, send to backend, display label.
class SoundIdentifyScreen extends StatefulWidget {
  const SoundIdentifyScreen({super.key});

  @override
  State<SoundIdentifyScreen> createState() => _SoundIdentifyScreenState();
}

class _SoundIdentifyScreenState extends State<SoundIdentifyScreen> {
  // Store file data in a platform-agnostic way
  Uint8List? _audioData;
  String? _audioFileName;
  String? _label;
  bool _loading = false;
  String? _error;
  final AudioPlayer _audioPlayer = AudioPlayer();

  /// Pick a WAV file from device.
  Future<void> _pickFile() async {
    try {
      setState(() {
        _error = null;
        _loading = true;
      });
      
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['wav'],
        withData: true,  // Get file bytes for web compatibility
      );

      if (result == null) {
        // User canceled the picker
        return;
      }

      final file = result.files.single;
      
      // Check file size (e.g., 10MB limit)
      const maxSize = 10 * 1024 * 1024; // 10MB
      if (file.size > maxSize) {
        throw Exception('File is too large. Maximum size is 10MB');
      }

      // Store the file data in memory
      if (file.bytes == null) {
        throw Exception('Failed to read file data');
      }

      setState(() {
        _audioData = file.bytes!;
        _audioFileName = file.name;
        _label = null; // Clear previous prediction
      });
    } catch (e) {
      setState(() {
        _error = 'Error selecting file: ${e.toString().replaceAll('Exception: ', '')}';
      });
      debugPrint('Error picking file: $e');
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  /// Play audio on web using the Web Audio API
  Future<void> _playAudioWeb(Uint8List audioData) async {
    try {
      debugPrint('Creating audio element for web playback');
      
      // Create an audio element
      final audio = html.AudioElement()
        ..src = ''
        ..autoplay = true;
      
      // Create a blob URL from the audio data
      final blob = html.Blob([audioData], 'audio/wav');
      final url = html.Url.createObjectUrl(blob);
      
      // Set the source and play
      audio.src = url;
      
      // Clean up when done
      audio.onEnded.listen((_) {
        html.Url.revokeObjectUrl(url);
        if (mounted) {
          setState(() {
            _loading = false;
          });
        }
      });
      
      // Handle errors
      audio.onError.listen((event) {
        debugPrint('Audio playback error: $event');
        html.Url.revokeObjectUrl(url);
        if (mounted) {
          setState(() {
            _error = 'Error playing audio';
            _loading = false;
          });
        }
      });
      
    } catch (e, stackTrace) {
      debugPrint('Error in _playAudioWeb: $e');
      debugPrint('Stack trace: $stackTrace');
      if (mounted) {
        setState(() {
          _error = 'Error playing audio: ${e.toString()}';
          _loading = false;
        });
      }
    }
  }

  /// Play the selected audio file.
  Future<void> _playAudio() async {
    if (_audioData == null || _audioData!.isEmpty) {
      setState(() {
        _error = 'No audio data available to play';
      });
      return;
    }
    
    try {
      setState(() {
        _loading = true;
        _error = null;
      });
      
      if (kIsWeb) {
        // For web, use the Audio API directly
        debugPrint('Playing audio on web');
        await _playAudioWeb(_audioData!);
      } else {
        // For mobile/desktop, save to a temporary file and play
        debugPrint('Playing audio from file (mobile/desktop)');
        final tempDir = await getTemporaryDirectory();
        final tempFile = File(path.join(tempDir.path, 'temp_audio_${DateTime.now().millisecondsSinceEpoch}.wav'));
        await tempFile.writeAsBytes(_audioData!);
        await _audioPlayer.stop();
        await _audioPlayer.play(DeviceFileSource(tempFile.path));
      }
      
    } catch (e, stackTrace) {
      debugPrint('Error playing audio: $e');
      debugPrint('Stack trace: $stackTrace');
      
      String errorMessage = 'Error playing audio';
      if (e is UnimplementedError) {
        errorMessage = 'Audio playback not supported on this platform';
      } else {
        errorMessage = 'Error: ${e.toString().replaceAll('Exception: ', '')}';
      }
      
      if (mounted) {
        setState(() {
          _error = errorMessage;
        });
      }
    } finally {
      if (mounted) {
        setState(() {
          _loading = false;
        });
      }
    }
  }

  /// Send audio to backend and get prediction results.
  Future<void> _identifySound() async {
    if (_audioData == null || _audioData!.isEmpty) {
      setState(() { 
        _error = 'No audio data available to identify';
      });
      return;
    }
    
    setState(() { 
      _loading = true; 
      _label = null; 
      _error = null; 
    });
    
    try {
      // Update the URI to match the backend route
      final uri = Uri.parse('http://localhost:8000/api/v1/ai/ai/predict');
      debugPrint('Sending request to: $uri');
      
      // Create a multipart request
      final request = http.MultipartRequest('POST', uri);
      
      // Add the audio file
      final multipartFile = http.MultipartFile.fromBytes(
        'file',
        _audioData!,
        filename: _audioFileName ?? 'audio_${DateTime.now().millisecondsSinceEpoch}.wav',
      );
      
      request.files.add(multipartFile);
      
      // Log request details
      debugPrint('Sending audio data (${_audioData!.length} bytes) to server...');
      
      // Send the request with timeout
      final completer = Completer<http.StreamedResponse>();
      final timer = Timer(const Duration(seconds: 30), () {
        if (!completer.isCompleted) {
          completer.completeError('Request timed out after 30 seconds');
        }
      });
      
      try {
        final streamedResponse = await request.send();
        timer.cancel();
        completer.complete(streamedResponse);
      } catch (e) {
        timer.cancel();
        rethrow;
      }
      
      // Get the response
      final response = await http.Response.fromStream(await completer.future);
      debugPrint('Response status: ${response.statusCode}');
      debugPrint('Response body: ${response.body}');
      
      if (response.statusCode == 200) {
        try {
          // Parse the JSON response
          final responseData = jsonDecode(response.body) as Map<String, dynamic>;
          
          if (responseData['success'] == true) {
            if (responseData['predictions'] != null && 
                (responseData['predictions'] as List).isNotEmpty) {
              // Get the first prediction (most confident)
              final prediction = (responseData['predictions'] as List).first;
              final className = prediction['class_name']?.toString() ?? 'Unknown';
              final confidence = prediction['confidence'] != null 
                  ? (double.tryParse(prediction['confidence'].toString()) ?? 0) * 100 
                  : 0.0;
                  
              setState(() { 
                _label = '$className (${confidence.toStringAsFixed(1)}% confidence)';
              });
            } else {
              setState(() { 
                _error = 'No predictions returned from the server';
              });
            }
          } else {
            final errorMsg = responseData['error']?.toString() ?? 'Unknown server error';
            setState(() { 
              _error = 'Server error: $errorMsg';
            });
          }
        } catch (e) {
          debugPrint('Error parsing response: $e');
          setState(() {
            _error = 'Error parsing server response: ${e.toString()}';
          });
        }
      } else {
        // Try to parse error message from response
        try {
          final errorData = jsonDecode(response.body) as Map<String, dynamic>;
          final errorMsg = errorData['error']?.toString() ?? 'Unknown error occurred';
          setState(() { 
            _error = 'Error: $errorMsg (Status: ${response.statusCode})'; 
          });
        } catch (e) {
          setState(() { 
            _error = 'Error: ${response.statusCode} - ${response.reasonPhrase}';
            if (response.body.isNotEmpty) {
              _error = '${_error!}\nResponse: ${response.body}';
            }
          });
        }
      }
    } on TimeoutException catch (e) {
      setState(() { 
        _error = 'Request timed out. Please try again.';
      });
      debugPrint('Request timed out: $e');
    } on http.ClientException catch (e) {
      setState(() { 
        _error = 'Network error: ${e.message}';
      });
      debugPrint('HTTP client error: $e');
    } on SocketException catch (e) {
      setState(() { 
        _error = 'Network error: Could not connect to the server. Please check your connection.';
      });
      debugPrint('Network error: $e');
    } on http.ClientException catch (e) {
      setState(() { 
        _error = 'Network error: ${e.message}';
      });
      debugPrint('HTTP client error: $e');
    } catch (e, stackTrace) {
      debugPrint('Error in _identifySound: $e');
      debugPrint('Stack trace: $stackTrace');
      setState(() { 
        _error = 'An error occurred: ${e.toString()}';
      });
    } finally {
      if (mounted) {
        setState(() { 
          _loading = false; 
        });
      }
    }
  }

  /// Builds the file info widget showing the selected file name
  Widget _buildFileInfo() {
    if (_audioData == null) {
      return const Text('No file selected');
    }
    return Text('Selected: ${_audioFileName ?? 'audio.wav'}');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('SoundTracker AI Identify')), 
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 500),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton.icon(
                  icon: const Icon(Icons.upload_file),
                  label: const Text('Pick WAV File'),
                  onPressed: _pickFile,
                ),
                const SizedBox(height: 16),
                _buildFileInfo(),
                if (_audioData != null) ...[
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      ElevatedButton.icon(
                        icon: const Icon(Icons.play_arrow),
                        label: const Text('Play'),
                        onPressed: _playAudio,
                      ),
                      const SizedBox(width: 16),
                      ElevatedButton.icon(
                        icon: const Icon(Icons.send),
                        label: const Text('Identify Sound'),
                        onPressed: _loading ? null : _identifySound,
                      ),
                    ],
                  ),
                ],
                if (_loading) const Padding(
                  padding: EdgeInsets.all(16),
                  child: CircularProgressIndicator(),
                ),
                if (_label != null) ...[
                  const SizedBox(height: 24),
                  Text('Prediction:', style: Theme.of(context).textTheme.titleMedium),
                  Text(_label!, style: Theme.of(context).textTheme.headlineSmall?.copyWith(color: Colors.blue)),
                ],
                if (_error != null) ...[
                  const SizedBox(height: 24),
                  Text(_error!, style: const TextStyle(color: Colors.red)),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
