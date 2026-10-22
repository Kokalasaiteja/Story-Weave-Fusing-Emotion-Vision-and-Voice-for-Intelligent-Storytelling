import 'package:flutter_test/flutter_test.dart';
import 'package:story_weave_mobile_app/main.dart';

void main() {
  testWidgets('Story Weave smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const StoryWeaveApp());
    expect(find.text('Story Weave'), findsWidgets);
  });
}
