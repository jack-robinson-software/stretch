import Foundation

// Product identity is independent of the companion character.
enum AppIdentity {
    static let name = "Stretch"
    static let bundleIdentifier = "dev.jackrobinsonsoftware.stretch.prototype"
    static let sourceURL = URL(string: "https://github.com/jack-robinson-software/stretch")!
    static var supportURL: URL? {
        guard let value = Bundle.main.object(forInfoDictionaryKey: "StretchSupportURL") as? String,
              let url = URL(string: value), url.scheme == "https",
              let host = url.host, ["buymeacoffee.com", "www.buymeacoffee.com"].contains(host),
              url.path.count > 1 else { return nil }
        return url
    }
}
struct CompanionCharacter {
    let id: String
    let name: String
    static let pip = CompanionCharacter(id: "pip", name: "Pip")
}


enum Clip: String, CaseIterable {
    case idle, wave, stretch, breathe, celebrate, walkOff, seatedReach, seatedTurn, seatedShoulders, seatedBreathe
    var frames: Int { switch self { case .idle: return 180; case .wave: return 120; case .stretch, .seatedReach: return 300; case .breathe, .seatedTurn, .seatedBreathe: return 240; case .celebrate: return 90; case .walkOff: return 165; case .seatedShoulders: return 180 } }
    var duration: TimeInterval { Double(frames) / 30 }
}
enum Kind: String { case seated, standing }
enum Movement: String, Equatable {
    case seatedReach, seatedTurn, seatedShoulders, seatedBreathe, standingStretch, standingBreathe
    var kind: Kind { rawValue.hasPrefix("seated") ? .seated : .standing }
    var clip: Clip { switch self { case .seatedReach: return .seatedReach; case .seatedTurn: return .seatedTurn; case .seatedShoulders: return .seatedShoulders; case .seatedBreathe: return .seatedBreathe; case .standingStretch: return .stretch; case .standingBreathe: return .breathe } }
    var title: String { switch self { case .seatedReach: return "Stay right there."; case .seatedTurn: return "A little change of view."; case .seatedShoulders: return "Let those shoulders go."; case .seatedBreathe: return "Room for a breath."; case .standingStretch: return "A little more room."; case .standingBreathe: return "Take your time." } }
    var detail: String { switch self { case .seatedReach: return "An easy reach.\nOne side, then the other."; case .seatedTurn: return "A gentle turn each way.\nNo need to leave your chair."; case .seatedShoulders: return "Small, slow shoulder rolls.\nFollow along at your own pace."; case .seatedBreathe, .standingBreathe: return "A slow breath in, and out.\nNothing else to do just now."; case .standingStretch: return "Reach up and ease to each side.\nMake a little space for yourself." } }
}
enum Phase: Equatable { case hidden, invitation, movement(Movement), completed(Kind), leaving }
struct Session {
    var phase: Phase = .hidden
    private var seatedIndex = 0
    private var standingIndex = 0
    mutating func invite() { phase = .invitation }
    @discardableResult mutating func choose(_ kind: Kind) -> Movement {
        let items: [Movement] = kind == .seated ? [.seatedReach, .seatedTurn, .seatedShoulders, .seatedBreathe] : [.standingStretch, .standingBreathe]
        let index = kind == .seated ? seatedIndex : standingIndex
        let movement = items[index % items.count]
        if kind == .seated { seatedIndex += 1 } else { standingIndex += 1 }
        phase = .movement(movement)
        return movement
    }
    mutating func finish() { if case .movement(let m) = phase { phase = .completed(m.kind) } }
    mutating func hide() { phase = .hidden }
}
enum WorkHours: String, CaseIterable {
    case anytime, nineToFive, nineToSix
    var label: String { switch self { case .anytime: return "Any time"; case .nineToFive: return "9 am – 5 pm"; case .nineToSix: return "9 am – 6 pm" } }
    var end: Int { self == .nineToFive ? 17 : 18 }
    func permits(_ date: Date, calendar: Calendar = .current) -> Bool { self == .anytime || (calendar.component(.hour, from: date) >= 9 && calendar.component(.hour, from: date) < end) }
}
struct Schedule {
    static func next(after date: Date, minutes: Int, hours: WorkHours, calendar: Calendar = .current) -> Date {
        let candidate = date.addingTimeInterval(Double(minutes) * 60)
        guard !hours.permits(candidate, calendar: calendar) else { return candidate }
        let morning = calendar.date(bySettingHour: 9, minute: 0, second: 0, of: candidate)!
        return candidate < morning ? morning : calendar.date(byAdding: .day, value: 1, to: morning)!
    }
}
final class Preferences {
    let defaults: UserDefaults
    init(_ defaults: UserDefaults = .standard) {
        self.defaults = defaults
        // Keep existing prototype preferences when moving to the product bundle ID.
        if defaults === UserDefaults.standard,
           defaults.persistentDomain(forName: AppIdentity.bundleIdentifier) == nil,
           let legacy = defaults.persistentDomain(forName: "dev.pip.companion.prototype") {
            defaults.setPersistentDomain(legacy, forName: AppIdentity.bundleIdentifier)
        }
        defaults.register(defaults: ["remindersEnabled": false, "interval": 45, "workHours": WorkHours.nineToSix.rawValue])
    }
    var enabled: Bool { get { defaults.bool(forKey: "remindersEnabled") } set { defaults.set(newValue, forKey: "remindersEnabled") } }
    var interval: Int { get { defaults.integer(forKey: "interval") } set { defaults.set(newValue, forKey: "interval") } }
    var hours: WorkHours { get { WorkHours(rawValue: defaults.string(forKey: "workHours") ?? "") ?? .nineToSix } set { defaults.set(newValue.rawValue, forKey: "workHours") } }
}
