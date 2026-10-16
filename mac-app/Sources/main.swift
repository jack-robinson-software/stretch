import AppKit
import ImageIO

func selfTest() {
    func expect(_ condition: @autoclosure () -> Bool,_ message: String) { if !condition() { print("FAIL:",message); exit(1) } }
    var session = Session(); session.invite(); expect(session.phase == .invitation,"invitation")
    expect(session.choose(.seated) == .seatedReach,"first seated choice")
    session.finish(); expect(session.phase == .completed(.seated),"completion retains the chair")
    expect(session.choose(.seated) == .seatedTurn,"another seated movement")
    expect(session.choose(.standing) == .standingStretch,"standing independent of seated choice")
    session.hide(); expect(session.phase == .hidden,"dismissal")
    var calendar = Calendar(identifier:.gregorian); calendar.timeZone = TimeZone(secondsFromGMT:0)!
    func date(_ h: Int,_ m: Int) -> Date { calendar.date(from:DateComponents(year:2026,month:10,day:16,hour:h,minute:m))! }
    expect(Schedule.next(after:date(10,0),minutes:45,hours:.nineToSix,calendar:calendar) == date(10,45),"normal interval")
    expect(Schedule.next(after:date(7,0),minutes:45,hours:.nineToSix,calendar:calendar) == date(9,0),"before working hours")
    expect(calendar.component(.day,from:Schedule.next(after:date(17,50),minutes:45,hours:.nineToSix,calendar:calendar)) == 17,"evening waits until tomorrow")
    let suite = "dev.jackrobinsonsoftware.stretch.tests.\(UUID().uuidString)"; let defaults = UserDefaults(suiteName:suite)!; let prefs = Preferences(defaults); expect(!prefs.enabled,"automatic reminders opt in"); defaults.removePersistentDomain(forName:suite)
    let onboardingSuite = "dev.jackrobinsonsoftware.stretch.onboarding.tests.\(UUID().uuidString)"
    let onboardingDefaults = UserDefaults(suiteName: onboardingSuite)!
    let onboardingPrefs = Preferences(onboardingDefaults)
    expect(!onboardingPrefs.hasCompletedOnboarding, "first run needs introduction")
    var draft = ReminderDraft(preferences: onboardingPrefs)
    draft.enabled = true; draft.interval = 30; draft.hours = .nineToFive
    expect(!onboardingPrefs.enabled && onboardingPrefs.interval == 45, "draft choices are not persisted early")
    onboardingPrefs.completeOnboarding(nil)
    expect(onboardingPrefs.hasCompletedOnboarding && !onboardingPrefs.enabled && onboardingPrefs.interval == 45, "skip keeps reminders off and respects dismissal")
    onboardingPrefs.completeOnboarding(draft)
    expect(onboardingPrefs.enabled && onboardingPrefs.interval == 30 && onboardingPrefs.hours == .nineToFive, "finish commits chosen rhythm")
    onboardingDefaults.removePersistentDomain(forName: onboardingSuite)
    onboardingDefaults.set(true, forKey: "hasMetPip")
    expect(onboardingPrefs.hasCompletedOnboarding, "returning prototype users are not forced into a tour")
    onboardingPrefs.hasCompletedOnboarding = false
    expect(!onboardingPrefs.hasCompletedOnboarding, "explicit completion flag takes precedence over legacy state")
    onboardingDefaults.removePersistentDomain(forName: onboardingSuite)
    guard let root = Bundle.main.resourceURL else { print("Missing resources"); exit(1) }
    for clip in Clip.allCases {
        let folder = root.appendingPathComponent("Clips/\(clip.rawValue)")
        let files = (try? FileManager.default.contentsOfDirectory(atPath:folder.path).filter{$0.hasSuffix(".png")}) ?? []
        expect(files.count == clip.frames,"\(clip) frame count")
        let url = folder.appendingPathComponent("0001.png")
        expect(CGImageSourceCreateWithURL(url as CFURL,nil) != nil,"\(clip) image decoding")
    }
    print("PASS: reminder hours, opt-in defaults, seated/standing flow, completion, dismissal, onboarding consent/migration, and all animation resources")
}
if CommandLine.arguments.contains("--self-test") { selfTest() } else {
    let app = NSApplication.shared
    let delegate = StretchApp(resources:Bundle.main.resourceURL!)
    app.delegate = delegate
    app.run()
}
