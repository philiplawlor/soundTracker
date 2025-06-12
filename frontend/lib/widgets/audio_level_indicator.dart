import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:frontend/providers/audio_provider.dart';
import 'package:percent_indicator/percent_indicator.dart';

class AudioLevelIndicator extends StatelessWidget {
  const AudioLevelIndicator({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AudioProvider>(
      builder: (context, audioProvider, _) {
        final dbLevel = audioProvider.dbLevel;
        final normalizedLevel = (dbLevel + 60) / 60; // Normalize to 0.0-1.0 range
        
        return Column(
          children: [
            // Circular progress indicator
            SizedBox(
              width: 200,
              height: 200,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  CircularPercentIndicator(
                    radius: 90,
                    lineWidth: 12,
                    percent: normalizedLevel.clamp(0.0, 1.0),
                    center: Text(
                      '${dbLevel.toStringAsFixed(1)} dB',
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    progressColor: _getLevelColor(normalizedLevel),
                    backgroundColor: Colors.grey[300]!,
                    circularStrokeCap: CircularStrokeCap.round,
                    animation: true,
                    animationDuration: 100,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            // DB scale
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _buildDbLabel(-60, dbLevel),
                  _buildDbLabel(-40, dbLevel),
                  _buildDbLabel(-20, dbLevel),
                  _buildDbLabel(0, dbLevel),
                ],
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildDbLabel(int db, double currentDb) {
    final isActive = currentDb >= db;
    return Column(
      children: [
        Container(
          width: 2,
          height: 8,
          color: isActive ? Colors.blue : Colors.grey,
        ),
        const SizedBox(height: 4),
        Text(
          '$db',
          style: TextStyle(
            fontSize: 12,
            color: isActive ? Colors.blue : Colors.grey,
            fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ],
    );
  }

  Color _getLevelColor(double level) {
    if (level < 0.3) return Colors.green;
    if (level < 0.6) return Colors.orange;
    return Colors.red;
  }
}
