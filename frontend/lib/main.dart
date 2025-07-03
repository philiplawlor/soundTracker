import 'dart:async';
import 'dart:io';
import 'dart:typed_data';
import 'dart:convert';
import 'dart:html' as html;
import 'package:flutter/foundation.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:file_picker/file_picker.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';
import 'package:permission_handler/permission_handler.dart';
import 'services/audio_recorder_service.dart';
import 'widgets/audio_waveform_painter.dart';

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
  // Audio recording and playback
  final AudioRecorderService _recorder = AudioRecorderService();
  final AudioPlayer _audioPlayer = AudioPlayer();
  
  // State variables
  Uint8List? _audioData;
  String? _audioFileName;
  String? _label;
  String? _error;
  bool _isLoading = false;
  
  @override
  void initState() {
    super.initState();
    _initRecorder();
  }
  
  @override
  void dispose() {
    _recorder.dispose();
    _audioPlayer.dispose();
    super.dispose();
  }
  
  Future<void> _initRecorder() async {
    // Request microphone permission
    final status = await Permission.microphone.request();
    if (status != PermissionStatus.granted) {
      setState(() {
        _error = 'Microphone permission not granted';
      });
    }
  }

  // Helper function to fetch audio data from blob URL (web only)
  Future<Uint8List> _fetchAudioFromBlob(String blobUrl) async {
    try {
      debugPrint('Fetching audio data from blob URL: $blobUrl');
      
      // Create a request to get the blob data
      final response = await http.get(Uri.parse(blobUrl));
      
      if (response.statusCode == 200) {
        debugPrint('Successfully fetched audio data, length: ${response.bodyBytes.length}');
        return response.bodyBytes;
      } else {
        debugPrint('Failed to fetch audio data: ${response.statusCode}');
        throw Exception('Failed to fetch audio data: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Error in _fetchAudioFromBlob: $e');
      rethrow;
    }
  }

  // Audio recording methods
  Future<void> _toggleRecording() async {
    try {
      if (_recorder.isRecording) {
        // Handle stopping the recording
        debugPrint('Stopping recording...');
        final path = await _recorder.stop();
        debugPrint('Recording stopped, path: $path');
        
        setState(() {
          _isLoading = true;
          _error = null;
        });
        
        try {
          if (kIsWeb) {
            debugPrint('Web platform detected, processing blob URL...');
            
            // On web, the path is actually a blob URL
            final blobUrl = path;
            
            // Fetch the audio data from the blob URL
            final audioData = await _fetchAudioFromBlob(blobUrl);
            
            // Create a WAV file header for the raw audio data
            // Note: This is a simplified version - in a real app, you'd want to properly
            // format the audio data with correct WAV headers
            final wavHeader = _createWavHeader(audioData.length);
            final wavData = Uint8List.fromList([...wavHeader, ...audioData]);
            
            setState(() {
              _audioData = wavData;
              _audioFileName = 'recording_${DateTime.now().millisecondsSinceEpoch}.wav';
              _label = null; // Clear previous result
              _error = null;
            });
            
            debugPrint('Web recording processed, audio data length: ${_audioData?.length}');
          } else {
            debugPrint('Mobile/desktop platform detected, reading file...');
            // For mobile/desktop, read the file bytes
            final file = File(path!);
            final bytes = await file.readAsBytes();
            
            setState(() {
              _audioData = bytes;
              _audioFileName = 'recording_${DateTime.now().millisecondsSinceEpoch}.wav';
              _label = null; // Clear previous result
              _error = null;
            });
            debugPrint('File read successfully, size: ${bytes.length} bytes');
          }
        } catch (e) {
          debugPrint('Error processing recording: $e');
          setState(() {
            _error = 'Error processing recording: ${e.toString()}';
          });
          return;
        } finally {
          setState(() {
            _isLoading = false;
          });
        }
      } else {
        // Start a new recording
        debugPrint('Starting new recording...');
        try {
          await _recorder.start();
          debugPrint('Recording started');
          setState(() {
            _error = null;
          });
        } catch (e) {
          debugPrint('Error starting recording: $e');
          setState(() {
            _error = 'Failed to start recording: ${e.toString()}';
          });
        }
      }
    } catch (e) {
      debugPrint('Error in _toggleRecording: $e');
      setState(() {
        _error = 'Failed to toggle recording: ${e.toString()}';
      });
    }
  }

  // Helper function to create a simple WAV header
  // This is a basic implementation and may need adjustments for your specific use case
  List<int> _createWavHeader(int dataLength) {
    // These values are placeholders - adjust based on your audio format
    final int sampleRate = 44100;  // 44.1 kHz
    final int numChannels = 1;     // Mono
    final int bitsPerSample = 16;  // 16-bit
    
    final int byteRate = sampleRate * numChannels * (bitsPerSample ~/ 8);
    final int blockAlign = numChannels * (bitsPerSample ~/ 8);
    final int totalDataLen = dataLength + 36;  // 36 is the size of the header
    
    // Create the WAV header
    final header = Uint8List(44);  // Standard WAV header is 44 bytes
    
    // RIFF header
    header.setRange(0, 4, [0x52, 0x49, 0x46, 0x46]);  // 'RIFF'
    header[4] = (totalDataLen) & 0xff;
    header[5] = (totalDataLen >> 8) & 0xff;
    header[6] = (totalDataLen >> 16) & 0xff;
    header[7] = (totalDataLen >> 24) & 0xff;
    header.setRange(8, 12, [0x57, 0x41, 0x56, 0x45]);  // 'WAVE'
    
    // fmt subchunk
    header.setRange(12, 16, [0x66, 0x6d, 0x74, 0x20]);  // 'fmt '
    header[16] = 16;  // Subchunk size
    header[20] = 1;   // Audio format (1 = PCM)
    header[22] = numChannels;
    header[24] = sampleRate & 0xff;
    header[25] = (sampleRate >> 8) & 0xff;
    header[26] = (sampleRate >> 16) & 0xff;
    header[27] = (sampleRate >> 24) & 0xff;
    header[28] = byteRate & 0xff;
    header[29] = (byteRate >> 8) & 0xff;
    header[30] = (byteRate >> 16) & 0xff;
    header[31] = (byteRate >> 24) & 0xff;
    header[32] = blockAlign;
    header[34] = bitsPerSample;
    
    // data subchunk
    header.setRange(36, 40, [0x64, 0x61, 0x74, 0x61]);  // 'data'
    header[40] = (dataLength) & 0xff;
    header[41] = (dataLength >> 8) & 0xff;
    header[42] = (dataLength >> 16) & 0xff;
    header[43] = (dataLength >> 24) & 0xff;
    
    return header;
  }

  Future<void> _pauseRecording() async {
    try {
      await _recorder.pause();
    } catch (e) {
      setState(() {
        _error = 'Failed to pause recording: ${e.toString()}';
      });
    }
  }

  Future<void> _resumeRecording() async {
    try {
      await _recorder.resume();
    } catch (e) {
      setState(() {
        _error = 'Failed to resume recording: ${e.toString()}';
      });
    }
  }

  // File handling methods
  Future<void> _pickFile() async {
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      final result = await FilePicker.platform.pickFiles(
        type: FileType.audio,
        allowMultiple: false,
      );

      if (result != null && result.files.single.bytes != null) {
        setState(() {
          _audioData = result.files.single.bytes!;
          _audioFileName = result.files.single.name;
          _label = null; // Clear previous result
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error selecting file: ${e.toString()}';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  // Audio playback methods
  Future<void> _playAudio() async {
    if (_audioData == null || _audioData!.isEmpty) {
      setState(() {
        _error = 'No audio data available to play';
      });
      return;
    }

    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      debugPrint('Playing audio, data length: ${_audioData!.length} bytes');
      
      if (kIsWeb) {
        debugPrint('Using web audio playback');
        await _playAudioWeb(_audioData!);
      } else {
        debugPrint('Using mobile/desktop audio playback');
        try {
          final tempDir = await getTemporaryDirectory();
          final file = File('${tempDir.path}/temp_playback_${DateTime.now().millisecondsSinceEpoch}.wav');
          debugPrint('Writing temporary file to: ${file.path}');
          await file.writeAsBytes(_audioData!);
          
          debugPrint('Starting audio playback...');
          await _audioPlayer.play(DeviceFileSource(file.path));
          debugPrint('Playback started');
        } catch (e) {
          debugPrint('Error in mobile/desktop playback: $e');
          rethrow;
        }
      }
    } catch (e) {
      debugPrint('Error in _playAudio: $e');
      setState(() {
        _error = 'Error playing audio: ${e.toString()}';
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _playAudioWeb(Uint8List audioData) async {
    try {
      debugPrint('Creating audio blob with ${audioData.length} bytes');
      
      // Create a Blob from the audio data
      final blob = html.Blob([audioData], 'audio/wav');
      
      // Create an object URL from the Blob
      final url = html.Url.createObjectUrlFromBlob(blob);
      debugPrint('Created object URL: $url');
      
      // Create a new audio element
      final audio = html.AudioElement()
        ..src = url
        ..autoplay = true
        ..controls = true; // Add controls for debugging
      
      // Add error handler
      audio.onError.listen((event) {
        debugPrint('Audio playback error: ${event.toString()}');
        if (mounted) {
          setState(() {
            _error = 'Audio playback error: ${event.toString()}';
          });
        }
      });
      
      // Add event listener for when audio is ready to play
      audio.onCanPlay.listen((event) {
        debugPrint('Audio is ready to play');
        try {
          final playPromise = audio.play();
          
          // Handle the play() promise
          if (playPromise != null) {
            playPromise.catchError((error) {
              debugPrint('Error playing audio: $error');
              if (mounted) {
                setState(() {
                  _error = 'Error playing audio: $error';
                });
              }
            });
          }
        } catch (e) {
          debugPrint('Exception during audio playback: $e');
          if (mounted) {
            setState(() {
              _error = 'Exception during audio playback: $e';
            });
          }
        }
      });
      
      // Clean up after playback
      audio.onEnded.listen((event) {
        debugPrint('Playback ended, cleaning up');
        html.Url.revokeObjectUrl(url);
      });
      
      // Add the audio element to the DOM (temporarily for debugging)
      // html.document.body?.children.add(audio);
      
      debugPrint('Audio element created and playback started');
    } catch (e) {
      debugPrint('Error in _playAudioWeb: $e');
      if (mounted) {
        setState(() {
          _error = 'Error playing audio on web: ${e.toString()}';
        });
      }
    }
  }

  // Sound identification
  Future<void> _identifySound() async {
    if (_audioData == null || _audioData!.isEmpty) {
      setState(() {
        _error = 'No audio data available to identify';
      });
      return;
    }

    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      // Create a multipart request with the correct API endpoint
      final uri = Uri.parse('http://localhost:8000/api/v1/ai/predict');
      debugPrint('Sending request to: ${uri.toString()}');
      final request = http.MultipartRequest('POST', uri);
      
      // Add the audio file
      request.files.add(http.MultipartFile.fromBytes(
        'file',
        _audioData!,
        filename: _audioFileName ?? 'audio.wav',
      ));

      // Send the request
      final response = await request.send();
      final responseBody = await response.stream.bytesToString();
      
      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(responseBody);
        setState(() {
          _label = jsonResponse['label'] ?? 'Unknown sound';
          if (jsonResponse['confidence'] != null) {
            _label = '${_label!} (${(jsonResponse['confidence'] * 100).toStringAsFixed(1)}%)';
          }
        });
      } else {
        setState(() {
          _error = 'Error identifying sound: ${response.reasonPhrase}';
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error identifying sound: ${e.toString()}';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Sound Identifier'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            // Status and error messages
            if (_error != null)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12.0),
                margin: const EdgeInsets.only(bottom: 16.0),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  borderRadius: BorderRadius.circular(8.0),
                  border: Border.all(color: Colors.red.shade200),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline, color: Colors.red),
                    const SizedBox(width: 8.0),
                    Expanded(
                      child: Text(
                        _error!,
                        style: const TextStyle(color: Colors.red),
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close, size: 20.0),
                      onPressed: () => setState(() => _error = null),
                      color: Colors.red,
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(),
                    ),
                  ],
                ),
              ),

            // Recording section
            Card(
              elevation: 4.0,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    const Text(
                      'Record Audio',
                      style: TextStyle(
                        fontSize: 20.0,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16.0),
                    
                    // Waveform visualization
                    StreamBuilder<RecordingState>(
                      stream: _recorder.state,
                      builder: (context, snapshot) {
                        final state = snapshot.data;
                        final isRecording = state?.isRecording ?? false;
                        final isPaused = state?.isPaused ?? false;
                        
                        return Column(
                          children: [
                            Container(
                              height: 100,
                              width: double.infinity,
                              decoration: BoxDecoration(
                                color: Colors.grey.shade100,
                                borderRadius: BorderRadius.circular(8.0),
                              ),
                              child: CustomPaint(
                                painter: AudioWaveformPainter(
                                  amplitude: state?.amplitude ?? 0.0,
                                  isRecording: isRecording && !isPaused,
                                ),
                              ),
                            ),
                            const SizedBox(height: 16.0),
                            
                            // Timer
                            Text(
                              state?.formattedDuration ?? '00:00',
                              style: const TextStyle(
                                fontSize: 24.0,
                                fontFamily: 'monospace',
                                fontWeight: FontWeight.bold,
                                color: Colors.blue,
                              ),
                            ),
                            
                            if (isPaused) ...[
                              const SizedBox(height: 8.0),
                              const Text(
                                'Paused',
                                style: TextStyle(
                                  color: Colors.orange,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ],
                        );
                      },
                    ),
                    
                    const SizedBox(height: 16.0),
                    
                    // Recording controls
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        // Record/Stop button
                        FloatingActionButton(
                          onPressed: _toggleRecording,
                          backgroundColor: _recorder.isRecording ? Colors.red : Colors.green,
                          child: Icon(_recorder.isRecording ? Icons.stop : Icons.mic),
                        ),
                        
                        const SizedBox(width: 20.0),
                        
                        // Pause/Resume button (only visible when recording)
                        if (_recorder.isRecording)
                          FloatingActionButton(
                            onPressed: _recorder.isPaused ? _resumeRecording : _pauseRecording,
                            backgroundColor: Colors.blue,
                            child: Icon(_recorder.isPaused ? Icons.play_arrow : Icons.pause),
                          ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 24.0),

            // File upload section
            Card(
              elevation: 4.0,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    const Text(
                      'Or Upload Audio File',
                      style: TextStyle(
                        fontSize: 20.0,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16.0),
                    
                    // File picker button
                    ElevatedButton.icon(
                      onPressed: _isLoading ? null : _pickFile,
                      icon: const Icon(Icons.upload_file),
                      label: const Text('Select Audio File'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 12.0, horizontal: 24.0),
                      ),
                    ),
                    
                    const SizedBox(height: 16.0),
                    
                    // Display selected file info
                    if (_audioFileName != null)
                      Text(
                        'Selected: $_audioFileName',
                        style: Theme.of(context).textTheme.bodySmall,
                        textAlign: TextAlign.center,
                      ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 24.0),

            // Playback and Identify section
            if (_audioData != null) ...[
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  // Play button
                  ElevatedButton.icon(
                    onPressed: _isLoading ? null : _playAudio,
                    icon: Icon(
                      _audioPlayer.state == PlayerState.playing ? Icons.pause : Icons.play_arrow,
                    ),
                    label: Text(_audioPlayer.state == PlayerState.playing ? 'Pause' : 'Play'),
                  ),
                  
                  // Identify button
                  ElevatedButton.icon(
                    onPressed: _isLoading ? null : _identifySound,
                    icon: _isLoading
                        ? const SizedBox(
                            width: 20.0,
                            height: 20.0,
                            child: CircularProgressIndicator(
                              strokeWidth: 2.0,
                              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          )
                        : const Icon(Icons.analytics),
                    label: Text(_isLoading ? 'Processing...' : 'Identify Sound'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 24.0),
              
              // Display identification result
              if (_label != null)
                Card(
                  color: Colors.green.shade50,
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      children: [
                        const Text(
                          'Identified Sound:',
                          style: TextStyle(
                            fontSize: 18.0,
                            fontWeight: FontWeight.bold,
                            color: const Color(0xFF2E7D32), // Dark green 800
                          ),
                        ),
                        const SizedBox(height: 8.0),
                        Text(
                          _label!,
                          style: const TextStyle(
                            fontSize: 20.0,
                            fontWeight: FontWeight.bold,
                            color: const Color(0xFF1B5E20), // Dark green 900
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),
                ),
            ] else ...[
              const Text(
                'Record or upload an audio file to identify sounds',
                style: TextStyle(color: Colors.grey),
                textAlign: TextAlign.center,
              ),
            ],

            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }
}
