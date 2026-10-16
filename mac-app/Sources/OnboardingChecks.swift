import AppKit

/// Native control checks, invoked only by --onboarding-self-test; uses isolated preferences.
func runOnboardingChecks(store: FrameStore) {
    func expect(_ condition: @autoclosure () -> Bool, _ message: String) {
        if !condition() { print("FAIL:", message); exit(1) }
    }
    func tap(_ controller: OnboardingController, _ title: String) {
        guard let button = controller.window?.contentView?.subviews.compactMap({ $0 as? NSButton }).first(where: { $0.title == title && !$0.isHidden }) else {
            print("FAIL: missing onboarding button", title); exit(1)
        }
        button.performClick(nil)
    }
    let suite = "dev.jackrobinsonsoftware.stretch.onboarding.ui.\(UUID().uuidString)"
    let defaults = UserDefaults(suiteName: suite)!
    defer { defaults.removePersistentDomain(forName: suite) }
    let prefs = Preferences(defaults)
    var completions = 0
    var hints = 0
    let controller = OnboardingController(store: store, companion: .pip, preferences: prefs, menuIcon: nil, revealMenuBar: { hints += 1 }) { draft in
        completions += 1
        prefs.completeOnboarding(draft)
    }
    expect(controller.step == .meet, "welcome starts at meet")
    controller.goBack()
    expect(controller.step == .meet, "back cannot precede welcome")
    tap(controller, "Meet Pip")
    expect(controller.step == .tryPause, "welcome action reaches trial")
    tap(controller, "Stay seated")
    tap(controller, "Get moving")
    tap(controller, "Choose my rhythm")
    expect(controller.step == .rhythm, "trial may be left before animation finishes")
    tap(controller, "Enable gentle nudges")
    expect(controller.draft.enabled && !prefs.enabled, "reminder checkbox changes draft only")
    if let intervals = controller.window?.contentView?.subviews.compactMap({ $0 as? NSSegmentedControl }).first {
        intervals.selectedSegment = 1
        NSApp.sendAction(intervals.action!, to: intervals.target, from: intervals)
    } else { expect(false, "interval control exists") }
    expect(controller.draft.interval == 30 && prefs.interval == 45, "interval changes stay in draft")
    tap(controller, "Where will Pip live?")
    expect(controller.step == .menuBar, "rhythm reaches menu-bar introduction")
    tap(controller, "Show me where")
    expect(hints == 1, "menu-bar hint is wired")
    tap(controller, "Back")
    expect(controller.draft.enabled && controller.draft.interval == 30, "back retains draft")
    tap(controller, "Where will Pip live?")
    tap(controller, "Let’s begin")
    controller.goNext()
    expect(completions == 1 && prefs.enabled && prefs.interval == 30 && prefs.hasCompletedOnboarding, "finish commits once")

    let replay = OnboardingController(store: store, companion: .pip, preferences: prefs, menuIcon: nil, revealMenuBar: {}) { draft in prefs.completeOnboarding(draft) }
    expect(replay.draft.enabled && replay.draft.interval == 30, "replay starts with existing rhythm")
    replay.goNext(); replay.goNext()
    tap(replay, "Enable gentle nudges")
    tap(replay, "Skip introduction")
    expect(prefs.enabled && prefs.interval == 30, "skipping replay discards draft and preserves saved settings")

    defaults.removePersistentDomain(forName: suite)
    let dismissed = OnboardingController(store: store, companion: .pip, preferences: prefs, menuIcon: nil, revealMenuBar: {}) { draft in prefs.completeOnboarding(draft) }
    dismissed.window?.performClose(nil)
    expect(prefs.hasCompletedOnboarding && !prefs.enabled, "closing introduction respects dismissal and leaves reminders off")
    print("PASS: native onboarding navigation, trial actions, draft settings, menu hint, back, completion, replay, skip and close")
}
