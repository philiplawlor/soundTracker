import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:file_picker/file_picker.dart';
import 'package:audioplayers/audioplayers.dart';

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
  File? _audioFile;
  String? _label;
  bool _loading = false;
  String? _error;
  final AudioPlayer _audioPlayer = AudioPlayer();

  /// Pick a WAV file from device.
  Future<void> _pickFile() async {
    setState(() { _error = null; });
    final result = await FilePicker.platform.pickFiles(type: FileType.custom, allowedExtensions: ['wav']);
    if (result != null && result.files.single.path != null) {
      setState(() { _audioFile = File(result.files.single.path!); });
    }
  }

  /// Play the selected audio file.
  Future<void> _playAudio() async {
    if (_audioFile == null) return;
    await _audioPlayer.play(DeviceFileSource(_audioFile!.path));
  }

  /// Send audio to backend and get label.
  Future<void> _identifySound() async {
    if (_audioFile == null) return;
    setState(() { _loading = true; _label = null; _error = null; });
    try {
      final uri = Uri.parse('http://localhost:8000/ai/identify');
      final request = http.MultipartRequest('POST', uri)
        ..files.add(await http.MultipartFile.fromPath('file', _audioFile!.path));
      final response = await request.send();
      final respStr = await response.stream.bytesToString();
      if (response.statusCode == 200) {
        final label = RegExp(r'"label"\s*:\s*"([^"]+)"').firstMatch(respStr)?.group(1);
        setState(() { _label = label ?? 'Unknown'; });
      } else {
        setState(() { _error = 'Error: ${response.statusCode}'; });
      }
    } catch (e) {
      setState(() { _error = 'Failed: $e'; });
    } finally {
      setState(() { _loading = false; });
    }
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
                if (_audioFile != null) ...[
                  Text('Selected: ${_audioFile!.path.split(Platform.pathSeparator).last}'),
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
      // changed in this State, which causes it to rerun the build method below
      // so that the display can reflect the updated values. If we changed
      // _counter without calling setState(), then the build method would not be
      // called again, and so nothing would appear to happen.
      _counter++;
    });
  }

  @override
  Widget build(BuildContext context) {
    // This method is rerun every time setState is called, for instance as done
    // by the _incrementCounter method above.
    //
    // The Flutter framework has been optimized to make rerunning build methods
    // fast, so that you can just rebuild anything that needs updating rather
    // than having to individually change instances of widgets.
    return Scaffold(
      appBar: AppBar(
        // TRY THIS: Try changing the color here to a specific color (to
        // Colors.amber, perhaps?) and trigger a hot reload to see the AppBar
        // change color while the other colors stay the same.
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        // Here we take the value from the MyHomePage object that was created by
        // the App.build method, and use it to set our appbar title.
        title: Text(widget.title),
      ),
      body: Center(
        // Center is a layout widget. It takes a single child and positions it
        // in the middle of the parent.
        child: Column(
          // Column is also a layout widget. It takes a list of children and
          // arranges them vertically. By default, it sizes itself to fit its
          // children horizontally, and tries to be as tall as its parent.
          //
          // Column has various properties to control how it sizes itself and
          // how it positions its children. Here we use mainAxisAlignment to
          // center the children vertically; the main axis here is the vertical
          // axis because Columns are vertical (the cross axis would be
          // horizontal).
          //
          // TRY THIS: Invoke "debug painting" (choose the "Toggle Debug Paint"
          // action in the IDE, or press "p" in the console), to see the
          // wireframe for each widget.
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text('You have pushed the button this many times:'),
            Text(
              '$_counter',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: const Icon(Icons.add),
      ), // This trailing comma makes auto-formatting nicer for build methods.
    );
  }
}
