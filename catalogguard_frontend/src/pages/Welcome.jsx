import React from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Sparkles, ShieldCheck, ScanSearch, GitCompareArrows, CheckCircle2, Search } from "lucide-react";
import HeadphonesA from "../components/illustrations/HeadphonesA";
import HeadphonesB from "../components/illustrations/HeadphonesB";
import WirelessEarbuds from "../components/illustrations/WirelessEarbuds";
import BluetoothSpeaker from "../components/illustrations/BluetoothSpeaker";

export default function Welcome() {
  return (
    <main className="landing-page">
      <header className="landing-nav">
        <Link to="/" className="landing-brand" aria-label="Duplicate Product Review Queue home">
          <span className="landing-brand-mark"><ShieldCheck size={23} /></span>
          <span>Duplicate Product <strong>Review Queue</strong></span>
        </Link>
        <nav className="landing-links" aria-label="Main navigation">
          <a href="#how-it-works">How it works</a>
          <a href="#features">Features</a>
          <a href="#about">About</a>
        </nav>
      </header>

      <section className="landing-hero" id="about">
        <div className="landing-glow landing-glow-one" />
        <div className="landing-glow landing-glow-two" />
        <div className="landing-hero-inner">
          <div className="landing-copy">
            <div className="landing-eyebrow"><span /> PRODUCT INFORMATION MANAGEMENT</div>
            <h1>One catalogue.<br />Clearer decisions.<br /><span>Fewer duplicates.</span></h1>
            <p className="landing-subtitle">Review possible duplicate products with confidence. Compare catalogue records, inspect matching evidence, and keep every decision in human hands.</p>
            <div className="landing-hero-actions">
              <Link to="/login" className="landing-primary">Login <ArrowRight size={17} /></Link>
              <Link to="/register" className="landing-secondary">Register <span>↗</span></Link>
            </div>
            <div className="landing-trust-row"><span><CheckCircle2 size={15} /> Human-reviewed decisions</span><span><ShieldCheck size={15} /> No automatic catalogue changes</span></div>
          </div>

          <div className="landing-visual" aria-label="Illustration of a duplicate product review">
            <div className="visual-orbit orbit-one" /><div className="visual-orbit orbit-two" />
            <div className="visual-top-chip"><Sparkles size={15} /> Smart duplicate review</div>
            <div className="visual-review-card">
              <div className="visual-card-head"><div><span className="visual-kicker">REVIEW QUEUE / CG-024</span><h3>Possible product match</h3></div><span className="visual-status">Needs review</span></div>
              <div className="visual-products">
                <div className="visual-product visual-product-a"><div className="product-art"><HeadphonesA /></div><span className="visual-product-label">CATALOGUE A</span><strong>AeroSound Wireless Headphones</strong><small>SKU · AS500-BLK</small></div>
                <div className="visual-match"><span>VS</span><div /></div>
                <div className="visual-product visual-product-b"><div className="product-art"><HeadphonesB /></div><span className="visual-product-label">CATALOGUE B</span><strong>AeroSound AS-500 Bluetooth Headphones</strong><small>SKU · AS500-BLK-2</small></div>
              </div>
              <div className="visual-score-row"><div><span className="visual-score-icon"><GitCompareArrows size={16} /></span><div><strong>Match confidence</strong><small>Based on product evidence</small></div></div><strong className="visual-score">92%</strong></div>
              <div className="visual-progress"><span /></div>
              <div className="visual-evidence"><span><CheckCircle2 size={14} /> Similar title</span><span><CheckCircle2 size={14} /> Same category</span><span className="evidence-caution"><ScanSearch size={14} /> Verify SKU</span></div>
              <div className="visual-card-actions"><span>Reviewer decision required</span><span className="visual-review-button">Review pair <ArrowRight size={13} /></span></div>
              <div className="hero-accent hero-accent-earbuds"><WirelessEarbuds /></div>
              <div className="hero-accent hero-accent-speaker"><BluetoothSpeaker /></div>
            </div>
            <div className="visual-float visual-float-left"><span className="float-icon"><ScanSearch size={17} /></span><span><strong>Evidence first</strong><small>Compare before deciding</small></span></div>
            <div className="visual-float visual-float-right"><span className="float-icon float-icon-purple"><ShieldCheck size={17} /></span><span><strong>Human in control</strong><small>Nothing merges automatically</small></span></div>
            <div className="visual-sparkle sparkle-one">✦</div><div className="visual-sparkle sparkle-two">✧</div>
          </div>
        </div>
        <div className="landing-bottom-note"><span>BUILT FOR CATALOGUE QUALITY</span><span className="note-line" /><span>DETECT · COMPARE · REVIEW</span></div>
      </section>

      <section className="landing-features" id="features">
        <div className="landing-section-heading"><span className="landing-eyebrow"><span /> A BETTER REVIEW WORKFLOW</span><h2>From possible match to informed decision.</h2><p>Bring duplicate candidates and the evidence behind them into one focused review experience.</p></div>
        <div className="landing-feature-grid" id="how-it-works">
          <article className="landing-feature"><span className="feature-icon feature-lilac"><Search size={21} /></span><h3>Find possible duplicates</h3><p>Bring likely duplicate pairs into a clear, prioritised review queue.</p><span className="feature-step">01 / DISCOVER</span></article>
          <article className="landing-feature"><span className="feature-icon feature-pink"><GitCompareArrows size={21} /></span><h3>Compare the evidence</h3><p>Review product details, matching signals, and differences side by side.</p><span className="feature-step">02 / INVESTIGATE</span></article>
          <article className="landing-feature"><span className="feature-icon feature-blue"><ShieldCheck size={21} /></span><h3>Keep decisions human</h3><p>Accept, reject, or defer a suggestion without automatic catalogue edits.</p><span className="feature-step">03 / DECIDE</span></article>
        </div>
        <footer className="landing-footer"><span className="landing-footer-brand"><ShieldCheck size={17} /> Duplicate Product Review Queue</span><span>Review carefully. Decide confidently.</span><Link to="/login">Login <ArrowRight size={14} /></Link></footer>
      </section>
    </main>
  );
}
