import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:frontend/providers/audio_provider.dart';

class ConnectionStatus extends StatelessWidget {
  const ConnectionStatus({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AudioProvider>(
      builder: (context, audioProvider, _) {
        final isConnected = audioProvider.isConnected;
        final error = audioProvider.connectionError;
        
        return Row(
          children: [
            Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                color: isConnected ? Colors.green : Colors.red,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 8),
            Text(
              isConnected ? 'Connected' : error ?? 'Disconnected',
              style: TextStyle(
                color: isConnected ? Colors.green : Colors.red,
                fontSize: 14,
              ),
            ),
          ],
        );
      },
    );
  }
}
