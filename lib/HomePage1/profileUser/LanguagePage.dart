import 'package:flutter/material.dart';

class LanguagePage extends StatelessWidget {
  const LanguagePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('langage'),
      ),
      body: const Center(
        child: Text('Here you can change the langauge'),
      ),
    );
  }
}