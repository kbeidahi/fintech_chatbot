import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:fintech_chatbot/main.dart';

void main() {
  testWidgets('FinAssist app renders login screen', (WidgetTester tester) async {
    await tester.pumpWidget(const FinAssistApp());
    await tester.pump();

    expect(find.text('FinAssist'), findsWidgets);
    expect(find.byType(TextField), findsAtLeastNWidgets(2));
  });
}
