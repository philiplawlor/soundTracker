import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:frontend/services/websocket_service.dart';
import 'package:frontend/providers/audio_provider.dart';
import 'package:frontend/screens/home_screen.dart';
import 'package:frontend/themes/app_theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize services
  final webSocketService = WebSocketService();
  
  runApp(
    MultiProvider(
      providers: [
        Provider<WebSocketService>(
          create: (_) => webSocketService,
          dispose: (_, service) => service.disconnect(),
        ),
        ChangeNotifierProvider<AudioProvider>(
          create: (context) => AudioProvider(
            context.read<WebSocketService>(),
          )..connect(),
        ),
      ],
      child: const SoundTrackerApp(),
    ),
  );
}

class SoundTrackerApp extends StatelessWidget {
  const SoundTrackerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SoundTracker',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      home: const HomeScreen(),
    );
  }
}
