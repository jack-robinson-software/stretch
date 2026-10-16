import AppKit

/// A short introduction using the same clips and player as the desktop companion.
final class OnboardingController: NSWindowController, NSWindowDelegate {
    enum Step: Int, CaseIterable { case meet, tryPause, rhythm, menuBar }
    private(set) var step: Step = .meet
    private(set) var draft: ReminderDraft
    private let store: FrameStore
    private let companion: CompanionCharacter
    private let menuIcon: NSImage?
    private let completed: (ReminderDraft?) -> Void
    private let revealMenuBar: () -> Void
    private let canvas = OnboardingCanvas(frame: NSRect(x: 0, y: 0, width: 640, height: 500))
    private var player: CharacterView?
    private var generation = 0
    private var hasFinished = false
    private var trialProgress: ProgressLine?
    private var trialNote: NSTextField?

    init(store: FrameStore, companion: CompanionCharacter, preferences: Preferences,
         menuIcon: NSImage?, revealMenuBar: @escaping () -> Void,
         completed: @escaping (ReminderDraft?) -> Void) {
        self.store = store
        self.companion = companion
        self.draft = ReminderDraft(preferences: preferences)
        self.menuIcon = menuIcon
        self.revealMenuBar = revealMenuBar
        self.completed = completed
        let window = NSWindow(contentRect: canvas.bounds, styleMask: [.titled, .closable, .miniaturizable], backing: .buffered, defer: false)
        window.title = "Welcome to \(AppIdentity.name)"
        window.titlebarAppearsTransparent = true
        window.backgroundColor = Palette.paper
        window.appearance = NSAppearance(named: .aqua)
        window.isReleasedWhenClosed = false
        super.init(window: window)
        window.contentView = canvas
        window.delegate = self
        window.center()
        render()
    }
    required init?(coder: NSCoder) { fatalError() }
    func present() {
        showWindow(nil)
        window?.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }
    @discardableResult private func text(_ value: String, _ frame: NSRect, font: NSFont, color: NSColor = Palette.cocoa) -> NSTextField {
        let view = label(value, font: font, color: color)
        view.frame = frame
        canvas.addSubview(view)
        return view
    }
    @discardableResult private func button(_ title: String, _ frame: NSRect, style: CompanionButton.Style = .secondary, action: Selector) -> CompanionButton {
        let view = CompanionButton(title, style: style, target: self, action: action)
        view.frame = frame
        canvas.addSubview(view)
        return view
    }
    private func render() {
        generation += 1
        let token = generation
        player?.stop()
        canvas.subviews.forEach { $0.removeFromSuperview() }
        trialProgress = nil
        trialNote = nil
        let names = ["MEET \(companion.name.uppercased())", "A LITTLE PAUSE", "YOUR RHYTHM", "FIND US AGAIN"]
        text(AppIdentity.name.uppercased(), NSRect(x: 36, y: 448, width: 160, height: 16), font: .systemFont(ofSize: 11, weight: .semibold), color: Palette.muted)
        let counter = text("\(step.rawValue + 1) OF 4 · \(names[step.rawValue])", NSRect(x: 330, y: 448, width: 274, height: 16), font: .systemFont(ofSize: 10, weight: .medium), color: Palette.muted)
        counter.alignment = .right
        let headings = ["A little pause.\nA little better.", "Try a little pause.", "At your own pace.", "A little company,\njust up here."]
        text(headings[step.rawValue], NSRect(x: 34, y: 326, width: 350, height: 96), font: serif(32))
        let hero = CharacterView(store: store)
        hero.frame = NSRect(x: 390, y: 170, width: 210, height: 252)
        canvas.addSubview(hero)
        player = hero
        var footer = "About a minute. No account needed."
        switch step {
        case .meet:
            text("Meet \(companion.name), your first companion.\nA friendly nudge to stretch or breathe,\nthen back to your day.", NSRect(x: 36, y: 241, width: 327, height: 76), font: .systemFont(ofSize: 14), color: Palette.muted)
            hero.play(.wave, repeats: 1) { [weak self, weak hero] in
                guard let self, self.generation == token else { return }
                hero?.play(.idle)
            }
        case .tryPause:
            text("Stay in your chair or get on your feet.\nFollow \(companion.name) only as far as feels\ncomfortable for you.", NSRect(x: 36, y: 241, width: 327, height: 76), font: .systemFont(ofSize: 14), color: Palette.muted)
            button("Stay seated", NSRect(x: 36, y: 185, width: 137, height: 38), action: #selector(trySeated))
            button("Get moving", NSRect(x: 182, y: 185, width: 137, height: 38), action: #selector(tryStanding))
            let progress = ProgressLine(frame: NSRect(x: 36, y: 166, width: 283, height: 3))
            canvas.addSubview(progress)
            trialProgress = progress
            trialNote = text("Pick a movement to try it.", NSRect(x: 36, y: 132, width: 300, height: 23), font: .systemFont(ofSize: 12), color: Palette.muted)
            hero.play(.idle)
            footer = "Try one, or continue. You can finish whenever you like."
        case .rhythm:
            text("A gentle nudge when it suits you.\nYou can always say ‘not now’.", NSRect(x: 36, y: 265, width: 327, height: 51), font: .systemFont(ofSize: 14), color: Palette.muted)
            text("A little nudge every", NSRect(x: 36, y: 232, width: 280, height: 20), font: .systemFont(ofSize: 12), color: Palette.muted)
            let intervals = NSSegmentedControl(labels: ["15m", "30m", "45m", "60m"], trackingMode: .selectOne, target: self, action: #selector(intervalChanged(_:)))
            intervals.frame = NSRect(x: 36, y: 198, width: 283, height: 29)
            intervals.selectedSegment = [15, 30, 45, 60].firstIndex(of: draft.interval) ?? 2
            canvas.addSubview(intervals)
            text("Working hours", NSRect(x: 36, y: 161, width: 280, height: 20), font: .systemFont(ofSize: 12), color: Palette.muted)
            let hours = NSPopUpButton(frame: NSRect(x: 33, y: 126, width: 289, height: 29), pullsDown: false)
            hours.addItems(withTitles: WorkHours.allCases.map(\.label))
            hours.selectItem(at: WorkHours.allCases.firstIndex(of: draft.hours) ?? 2)
            hours.target = self
            hours.action = #selector(hoursChanged(_:))
            canvas.addSubview(hours)
            let enabled = NSButton(checkboxWithTitle: "Enable gentle nudges", target: self, action: #selector(enabledChanged(_:)))
            enabled.font = .systemFont(ofSize: 13)
            enabled.state = draft.enabled ? .on : .off
            enabled.frame = NSRect(x: 36, y: 95, width: 300, height: 24)
            canvas.addSubview(enabled)
            hero.play(.breathe)
            footer = "Off unless you choose it. Change this anytime in Settings."
        case .menuBar:
            text("Look for the little bean in your Mac’s\nmenu bar. Bring \(companion.name) back, snooze\nor change your settings from there.", NSRect(x: 36, y: 241, width: 327, height: 76), font: .systemFont(ofSize: 14), color: Palette.muted)
            button("Show me where", NSRect(x: 36, y: 185, width: 155, height: 38), action: #selector(showMenuBar))
            let summary = draft.enabled ? "A nudge every \(draft.interval) minutes.\n\(draft.hours.label), every day." : "On demand for now.\nSay hello whenever you like."
            text(summary, NSRect(x: 36, y: 127, width: 320, height: 43), font: .systemFont(ofSize: 12), color: Palette.muted)
            let icon = NSImageView(frame: NSRect(x: 466, y: 408, width: 22, height: 24))
            icon.image = menuIcon
            icon.contentTintColor = Palette.cocoa
            canvas.addSubview(icon)
            hero.play(.idle)
            footer = "Your menu-bar companion. Quietly there when you need it."
        }
        text(footer, NSRect(x: 36, y: step == .rhythm ? 77 : 92, width: 568, height: 17), font: .systemFont(ofSize: 11), color: Palette.muted)
        let back = button("Back", NSRect(x: 36, y: 28, width: 72, height: 40), style: .text, action: #selector(goBack))
        back.isHidden = step == .meet
        let skip = button("Skip introduction", NSRect(x: step == .meet ? 36 : 119, y: 28, width: 139, height: 40), style: .text, action: #selector(skip))
        skip.keyEquivalent = "\u{1b}"
        let nextTitle = ["Meet \(companion.name)", "Choose my rhythm", "Where will \(companion.name) live?", "Let’s begin"][step.rawValue]
        let next = button(nextTitle, NSRect(x: 414, y: 28, width: 190, height: 40), style: .primary, action: #selector(goNext))
        next.keyEquivalent = "\r"
        window?.makeFirstResponder(next)
        NSAccessibility.post(element: canvas, notification: .layoutChanged)
    }
    @objc func goNext() {
        guard !hasFinished else { return }
        if step == .menuBar { finish(draft); return }
        step = Step(rawValue: step.rawValue + 1)!
        render()
    }
    @objc func goBack() {
        guard !hasFinished else { return }
        guard let previous = Step(rawValue: step.rawValue - 1) else { return }
        step = previous
        render()
    }
    @objc func skip() { finish(nil) }
    private func finish(_ value: ReminderDraft?) {
        guard !hasFinished else { return }
        hasFinished = true
        player?.stop()
        generation += 1
        window?.orderOut(nil)
        completed(value)
    }
    func windowShouldClose(_ sender: NSWindow) -> Bool { finish(nil); return true }
    @objc private func intervalChanged(_ sender: NSSegmentedControl) { draft.interval = [15, 30, 45, 60][max(0, sender.selectedSegment)] }
    @objc private func hoursChanged(_ sender: NSPopUpButton) { draft.hours = WorkHours.allCases[max(0, sender.indexOfSelectedItem)] }
    @objc private func enabledChanged(_ sender: NSButton) { draft.enabled = sender.state == .on }
    @objc private func showMenuBar() { revealMenuBar() }
    @objc private func trySeated() { tryMovement(.seatedReach) }
    @objc private func tryStanding() { tryMovement(.stretch) }
    private func tryMovement(_ clip: Clip) {
        generation += 1
        let token = generation
        trialProgress?.fraction = 0
        trialNote?.stringValue = clip == .seatedReach ? "An easy reach, one side at a time." : "Reach up, then ease to each side."
        player?.progress = { [weak self] value in self?.trialProgress?.fraction = value }
        player?.play(clip, repeats: 1) { [weak self] in
            guard let self, self.generation == token else { return }
            self.trialNote?.stringValue = "Nicely done. A little pause counts."
            if clip == .seatedReach { self.player?.freeze(.seatedReach) } else { self.player?.play(.idle) }
        }
    }
    // Capture the actual native views without changing stored preferences.
    func capture(to directory: URL) {
        try? FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        for item in Step.allCases {
            step = item
            render()
            player?.freeze(item == .tryPause ? .seatedReach : .wave, frame: item == .tryPause ? 78 : 50)
            canvas.layoutSubtreeIfNeeded()
            canvas.displayIfNeeded()
            if let rep = canvas.bitmapImageRepForCachingDisplay(in: canvas.bounds) {
                canvas.cacheDisplay(in: canvas.bounds, to: rep)
                if let data = rep.representation(using: .png, properties: [:]) {
                    try? data.write(to: directory.appendingPathComponent("onboarding-\(item.rawValue + 1).png"))
                }
            }
        }
        player?.stop()
    }
}

final class OnboardingCanvas: NSView {
    override func draw(_ dirtyRect: NSRect) { Palette.paper.setFill(); bounds.fill() }
}
