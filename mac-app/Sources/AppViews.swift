import AppKit
import QuartzCore
import ImageIO

extension NSColor {
    convenience init(hex: UInt32, alpha: CGFloat = 1) { self.init(srgbRed: CGFloat((hex >> 16) & 255)/255, green: CGFloat((hex >> 8) & 255)/255, blue: CGFloat(hex & 255)/255, alpha: alpha) }
}
enum Palette {
    static let paper = NSColor(hex: 0xFFF8ED)
    static let cocoa = NSColor(hex: 0x593A28)
    static let muted = NSColor(hex: 0x8A705B)
    static let orange = NSColor(hex: 0xB9512B)
    static let sage = NSColor(hex: 0xE4EADB)
    static let line = NSColor(hex: 0xDDCDB9)
}
func label(_ text: String, font: NSFont, color: NSColor = Palette.cocoa) -> NSTextField {
    let v = NSTextField(wrappingLabelWithString: text); v.font = font; v.textColor = color; v.isSelectable = false; v.lineBreakMode = .byWordWrapping; return v
}
func serif(_ size: CGFloat) -> NSFont { NSFont(name: "Georgia", size: size) ?? .systemFont(ofSize: size, weight: .medium) }

final class CompanionButton: NSButton {
    enum Style { case primary, secondary, text }
    var style: Style = .secondary
    private var hovering = false
    private var area: NSTrackingArea?
    init(_ title: String, style: Style = .secondary, target: AnyObject?, action: Selector?) {
        super.init(frame: .zero); self.title = title; self.style = style; self.target = target; self.action = action
        isBordered = false; bezelStyle = .rounded; font = .systemFont(ofSize: 12, weight: .medium); setButtonType(.momentaryPushIn)
        setAccessibilityLabel(title)
    }
    required init?(coder: NSCoder) { fatalError() }
    override func acceptsFirstMouse(for event: NSEvent?) -> Bool { true }
    override func updateTrackingAreas() {
        super.updateTrackingAreas(); if let area { removeTrackingArea(area) }
        let next = NSTrackingArea(rect: bounds, options: [.mouseEnteredAndExited, .activeAlways, .inVisibleRect], owner: self); addTrackingArea(next); area = next
    }
    override func mouseEntered(with event: NSEvent) { hovering = true; needsDisplay = true }
    override func mouseExited(with event: NSEvent) { hovering = false; needsDisplay = true }
    override func draw(_ dirtyRect: NSRect) {
        let pressed = isHighlighted
        if style != .text {
            let fill: NSColor = style == .primary ? Palette.orange : Palette.sage
            (pressed ? fill.blended(withFraction: 0.12, of: .black)! : hovering ? fill.blended(withFraction: 0.07, of: .white)! : fill).setFill()
            NSBezierPath(roundedRect: bounds.insetBy(dx: 0.5, dy: 0.5), xRadius: 9, yRadius: 9).fill()
        }
        let color = style == .primary ? Palette.paper : style == .text ? Palette.muted : Palette.cocoa
        let attrs: [NSAttributedString.Key: Any] = [.font: font ?? NSFont.systemFont(ofSize: 12), .foregroundColor: isEnabled ? color : color.withAlphaComponent(0.4)]
        let s = NSAttributedString(string: title, attributes: attrs); let size = s.size()
        s.draw(at: NSPoint(x: (bounds.width-size.width)/2, y: (bounds.height-size.height)/2-0.5))
        if window?.firstResponder === self { Palette.orange.setStroke(); let p = NSBezierPath(roundedRect: bounds.insetBy(dx: 2, dy: 2), xRadius: 7, yRadius: 7); p.lineWidth = 1; p.stroke() }
    }
}
final class ProgressLine: NSView {
    var fraction: CGFloat = 0 { didSet { needsDisplay = true } }
    override func draw(_ rect: NSRect) {
        Palette.line.withAlphaComponent(0.65).setFill(); NSBezierPath(roundedRect: bounds, xRadius: 1.5, yRadius: 1.5).fill()
        Palette.orange.withAlphaComponent(0.7).setFill(); NSBezierPath(roundedRect: NSRect(x: 0, y: 0, width: bounds.width*max(0,min(1,fraction)), height: bounds.height), xRadius: 1.5, yRadius: 1.5).fill()
    }
}
final class SpeechBubble: NSView {
    let heading = label("Fancy a little stretch?", font: serif(18))
    let detail = label("Take a moment, your way.", font: .systemFont(ofSize: 12.5), color: Palette.muted)
    let eyebrow = label(CompanionCharacter.pip.name.uppercased(), font: .systemFont(ofSize: 10, weight: .semibold), color: Palette.muted)
    let footer = label("", font: .systemFont(ofSize: 10), color: Palette.muted)
    let first: CompanionButton
    let second: CompanionButton
    let later: CompanionButton
    let progress = ProgressLine()
    init(target: AnyObject, first: Selector, second: Selector, later: Selector) {
        self.first = CompanionButton("Stay seated", style: .primary, target: target, action: first)
        self.second = CompanionButton("Get moving", style: .secondary, target: target, action: second)
        self.later = CompanionButton("Not now", style: .text, target: target, action: later)
        super.init(frame: NSRect(x: 0, y: 58, width: 282, height: 192))
        for v in [eyebrow,heading,detail,self.first,self.second,self.later,progress,footer] { addSubview(v) }
        eyebrow.frame = NSRect(x: 28,y: 150,width: 222,height: 14)
        heading.frame = NSRect(x: 28,y: 115,width: 225,height: 30)
        detail.frame = NSRect(x: 28,y: 80,width: 224,height: 33)
        self.first.frame = NSRect(x: 28,y: 41,width: 108,height: 32)
        self.second.frame = NSRect(x: 143,y: 41,width: 108,height: 32)
        self.later.frame = NSRect(x: 85,y: 15,width: 108,height: 21)
        progress.frame = NSRect(x: 28,y: 79,width: 222,height: 2)
        footer.frame = NSRect(x: 28,y: 18,width: 222,height: 14); footer.alignment = .center
        progress.isHidden = true; footer.isHidden = true
    }
    required init?(coder: NSCoder) { fatalError() }
    override func acceptsFirstMouse(for event: NSEvent?) -> Bool { true }
    override func draw(_ dirtyRect: NSRect) {
        let p = NSBezierPath()
        p.move(to:NSPoint(x:30,y:12)); p.line(to:NSPoint(x:248,y:12)); p.curve(to:NSPoint(x:266,y:30),controlPoint1:NSPoint(x:258,y:12),controlPoint2:NSPoint(x:266,y:20))
        p.line(to:NSPoint(x:266,y:76)); p.curve(to:NSPoint(x:280,y:82),controlPoint1:NSPoint(x:270,y:79),controlPoint2:NSPoint(x:275,y:82)); p.curve(to:NSPoint(x:266,y:98),controlPoint1:NSPoint(x:274,y:86),controlPoint2:NSPoint(x:269,y:92))
        p.line(to:NSPoint(x:266,y:162)); p.curve(to:NSPoint(x:248,y:180),controlPoint1:NSPoint(x:266,y:172),controlPoint2:NSPoint(x:258,y:180)); p.line(to:NSPoint(x:30,y:180)); p.curve(to:NSPoint(x:12,y:162),controlPoint1:NSPoint(x:20,y:180),controlPoint2:NSPoint(x:12,y:172)); p.line(to:NSPoint(x:12,y:30)); p.curve(to:NSPoint(x:30,y:12),controlPoint1:NSPoint(x:12,y:20),controlPoint2:NSPoint(x:20,y:12)); p.close()
        NSGraphicsContext.saveGraphicsState(); let shadow = NSShadow(); shadow.shadowColor = NSColor(hex: 0x4C3021,alpha: 0.13); shadow.shadowBlurRadius = 9; shadow.shadowOffset = NSSize(width: 0,height: -2); shadow.set(); Palette.paper.setFill(); p.fill(); NSGraphicsContext.restoreGraphicsState()
        Palette.line.withAlphaComponent(0.7).setStroke(); p.lineWidth = 0.6; p.stroke()
    }
    func show(_ phase: Phase) {
        first.isHidden = false; second.isHidden = false; later.isHidden = true; footer.isHidden = true; progress.isHidden = true
        switch phase {
        case .invitation:
            heading.stringValue = "Fancy a little stretch?"; detail.stringValue = "Take a moment, your way."; first.title = "Stay seated"; second.title = "Get moving"; first.style = .primary; second.style = .secondary; later.isHidden = false
        case .movement(let m):
            heading.stringValue = m.title; detail.stringValue = m.detail; first.title = "Another"; second.title = "All done"; first.style = .secondary; second.style = .primary; progress.isHidden = false; footer.isHidden = false; footer.stringValue = "Finish whenever you like."
        case .completed:
            heading.stringValue = "Nicely done."; detail.stringValue = "A little pause counts.\nSee you in a while."; first.title = "Another"; second.title = "Back to it"; first.style = .secondary; second.style = .primary
        default: break
        }
        first.setAccessibilityLabel(first.title); second.setAccessibilityLabel(second.title); first.needsDisplay = true; second.needsDisplay = true
    }
}
final class FrameImage: NSObject { let image: CGImage; init(_ image: CGImage) { self.image = image } }
final class FrameStore {
    let resources: URL
    private let cache = NSCache<NSString, FrameImage>()
    init(_ resources: URL) { self.resources = resources; cache.countLimit = 28 }
    func image(_ clip: Clip, _ index: Int) -> CGImage? {
        let key = "\(clip.rawValue)/\(index)" as NSString
        if let value = cache.object(forKey: key) { return value.image }
        let url = resources.appendingPathComponent("Clips/\(clip.rawValue)/\(String(format: "%04d",index+1)).png")
        guard let source = CGImageSourceCreateWithURL(url as CFURL,nil), let image = CGImageSourceCreateImageAtIndex(source,0,[kCGImageSourceShouldCacheImmediately:true] as CFDictionary) else { return nil }
        cache.setObject(FrameImage(image),forKey:key); return image
    }
}
final class CharacterView: NSView {
    let store: FrameStore
    var image: CGImage?
    private var previous: CGImage?
    private var transition = CACurrentMediaTime()-1
    private var timer: Timer?
    private var started: CFTimeInterval = 0
    private var playing: Clip = .idle
    private var repeats = 0
    private var completion: (() -> Void)?
    var progress: ((Double) -> Void)?
    init(store: FrameStore) { self.store = store; super.init(frame: NSRect(x: 276,y: 22,width: 160,height: 192)) }
    required init?(coder: NSCoder) { fatalError() }
    override var isOpaque: Bool { false }
    func play(_ clip: Clip, repeats: Int = 0, completion: (() -> Void)? = nil) {
        timer?.invalidate(); self.previous = image; transition = CACurrentMediaTime(); playing = clip; self.repeats = repeats; self.completion = completion; started = CACurrentMediaTime(); image = store.image(clip,0); needsDisplay = true
        let t = Timer(timeInterval: 1/30, repeats: true) { [weak self] _ in self?.tick() }; timer = t; RunLoop.main.add(t,forMode:.common)
    }
    func freeze(_ clip: Clip, frame: Int = 0) { timer?.invalidate(); timer = nil; previous = nil; transition = CACurrentMediaTime(); image = store.image(clip,frame); needsDisplay = true }
    func stop() { timer?.invalidate(); timer = nil; completion = nil }
    private func tick() {
        let elapsed = CACurrentMediaTime()-started
        if repeats > 0 && elapsed >= playing.duration*Double(repeats) {
            image = store.image(playing,playing.frames-1); needsDisplay = true; timer?.invalidate(); timer = nil; progress?(1); let callback = completion; completion = nil; callback?(); return
        }
        let frame = Int(elapsed*30) % playing.frames
        image = store.image(playing,frame); needsDisplay = true
        if repeats > 0 { progress?(elapsed/(playing.duration*Double(repeats))) }
    }
    override func draw(_ rect: NSRect) {
        guard let context = NSGraphicsContext.current?.cgContext else { return }
        context.interpolationQuality = .high
        let blend = min(1,(CACurrentMediaTime()-transition)/0.18)
        if let previous, blend < 1 { context.setAlpha(1-blend); context.draw(previous,in:bounds) }
        if let image { context.setAlpha(previous == nil ? 1 : blend); context.draw(image,in:bounds) }
    }
}
final class CompanionRoot: NSView {
    override var isOpaque: Bool { false }
    override func acceptsFirstMouse(for event: NSEvent?) -> Bool { true }
}
final class CompanionPanel: NSPanel {
    override var canBecomeKey: Bool { true }
    override var canBecomeMain: Bool { false }
}
