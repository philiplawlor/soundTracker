import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:frontend/providers/audio_provider.dart';

class DeviceDropdown extends StatefulWidget {
  const DeviceDropdown({super.key});

  @override
  State<DeviceDropdown> createState() => _DeviceDropdownState();
}

class _DeviceDropdownState extends State<DeviceDropdown> {
  int? _selectedDeviceId;

  @override
  Widget build(BuildContext context) {
    return Consumer<AudioProvider>(
      builder: (context, audioProvider, _) {
        final devices = audioProvider.devices;
        
        // If no device is selected but we have devices, select the first one
        if (_selectedDeviceId == null && devices.isNotEmpty) {
          WidgetsBinding.instance.addPostFrameCallback((_) {
            setState(() {
              _selectedDeviceId = devices[0]['id'];
            });
          });
        }

        return Card(
          elevation: 2,
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text(
                  'Available Audio Devices',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
                const SizedBox(height: 8),
                if (devices.isEmpty)
                  const Text('No audio devices found')
                else
                  DropdownButtonFormField<int>(
                    value: _selectedDeviceId,
                    decoration: const InputDecoration(
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    ),
                    items: devices.map<DropdownMenuItem<int>>((device) {
                      return DropdownMenuItem<int>(
                        value: device['id'],
                        child: Text(
                          device['name'] ?? 'Unknown Device',
                          overflow: TextOverflow.ellipsis,
                        ),
                      );
                    }).toList(),
                    onChanged: (int? newValue) {
                      if (newValue != null) {
                        setState(() {
                          _selectedDeviceId = newValue;
                        });
                        // If audio is currently being captured, restart with new device
                        if (audioProvider.currentStatus?['is_capturing'] == true) {
                          audioProvider.startCapture(newValue);
                        }
                      }
                    },
                  ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    IconButton(
                      icon: const Icon(Icons.refresh),
                      tooltip: 'Refresh devices',
                      onPressed: audioProvider.refreshDevices,
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
