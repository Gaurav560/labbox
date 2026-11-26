import { useEffect, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../auth";
import Logo from "../components/Logo";
import { Copyright, SiteLinks } from "../components/SiteFooter";
import { SITE } from "../site";
import { useTheme } from "../theme";

// FAQs, Privacy policy and Terms of Service: public pages in one simple reading layout.

function InfoLayout({ title, intro, children }: { title: string; intro?: ReactNode; children: ReactNode }) {
  const { user } = useAuth();
  const { theme, toggle } = useTheme();
  useEffect(() => {
    document.title = `${title} · ${SITE.full}`;
    window.scrollTo(0, 0);
  }, [title]);
  return (
    <div className="info">
      <header className="info-header">
        <Logo to="/" />
        <span className="spacer" />
        <button className="btn btn-small btn-ghost" onClick={toggle} aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}>
          {theme === "dark" ? "☀" : "☾"}
        </button>
        {user ? (
          <Link className="btn btn-small btn-primary" to="/labs">Your labs</Link>
        ) : (
          <Link className="btn btn-small btn-ghost" to="/login">Log in</Link>
        )}
      </header>
      <main className="info-main">
        <article className="info-article">
          <h1>{title}</h1>
          {intro && <div className="info-intro">{intro}</div>}
          {children}
        </article>
      </main>
      <footer className="info-footer">
        <SiteLinks />
        <Copyright />
      </footer>
    </div>
  );
}

const mail = <a href={`mailto:${SITE.contactEmail}`}>{SITE.contactEmail}</a>;

/** Certificates (owner, 27 November): moved here from the home page's certificate section, plus how to check one. */
export const CERT_FAQS: { q: string; a: ReactNode }[] = [
  {
    q: "How do I get a certificate?",
    a: <p>Pass 80% of a lab's tasks. The check that gets you there makes your certificate: no form, no waiting. The first time, you type your full name as it should appear; later certificates use it by themselves.</p>,
  },
  {
    q: "Does my certificate have its own link?",
    a: <p>Yes. Every certificate gets an address of its own, made automatically, that anyone can open without logging in. You can hide it at any time from its page, and correct a mistake in the name once.</p>,
  },
  {
    q: "What does a certificate show?",
    a: <p>Proof, not a badge: your name, the lab, the date, how many of its tasks you passed on a real machine, how many chapters it has, and the skills you practised.</p>,
  },
  {
    q: "How can someone check that a certificate is real?",
    a: <p>Scan the QR code on it, or type its 8-character ID at <a href="/verify">/verify</a>. That page shows what our server has on record for that ID, so an edited picture shows up as a mismatch.</p>,
  },
];

export const FAQS: { q: string; a: ReactNode }[] = [
  {
    q: `What is ${SITE.product}?`,
    a: <p>Hands-on labs for programming, frameworks, databases and DevOps. Each lab gives you a real Linux machine in your browser with an editor and a terminal, and walks you through small steps: read a little, guess what happens, try it, and check your work.</p>,
  },
  {
    q: "Do I need to install anything?",
    a: <p>No. Everything runs in the browser. Your lab machine runs on our servers, already set up with the right tools (Python, Java, Node, Go, Postgres and so on).</p>,
  },
  {
    q: "Is it free?",
    a: <p>Yes, while we are in early access every lab is free. If that changes, we will say so clearly before you are asked to pay for anything.</p>,
  },
  {
    q: "What do I need to know before I start?",
    a: <p>Every lab shows its level and how long it takes. Beginner labs start from zero and explain every new idea before you use it.</p>,
  },
  {
    q: "What happens to my code?",
    a: <p>Your files stay in your workspace between visits. The machine stops when you have been away for a while and starts again when you come back. <strong>Reset</strong> gives you a fresh copy of the lab if you want to start over.</p>,
  },
  {
    q: "How are my answers checked?",
    a: <p>When you press <strong>Check</strong>, hidden tests run against a clean copy of your files. If something fails you see what the test expected next to what your code gave.</p>,
  },
  ...CERT_FAQS,
  {
    q: "Do hints cost anything?",
    a: <p>Hints are always there when you are stuck. Each one you open lowers the XP for that task a little (to 80%, then 60%, then 40%), so you always still earn something.</p>,
  },
  {
    q: "How do streaks work?",
    a: <p>Earn at least 20 XP in a day to keep your streak going. You get one freeze per week that covers a single missed day, so a busy day does not break it.</p>,
  },
  {
    q: "Can I use it on my phone?",
    a: <p>You can read lessons and answer questions on a phone. For writing code and using the terminal, a laptop or desktop works much better.</p>,
  },
  {
    q: "I found a bug or something is broken.",
    a: <p>Sorry about that. Write to {mail} with the lab name and what you saw, and we will look into it.</p>,
  },
];

export function FaqPage() {
  return (
    <InfoLayout title="FAQs" intro={<p>Quick answers about how {SITE.product} labs work. Something missing? Write to {mail}.</p>}>
      <div className="faq-list">
        {FAQS.map((f) => (
          <details key={f.q} className="faq">
            <summary>{f.q}</summary>
            <div className="faq-a">{f.a}</div>
          </details>
        ))}
      </div>
    </InfoLayout>
  );
}

export function PrivacyPage() {
  return (
    <InfoLayout title="Privacy policy" intro={<p className="muted">Last updated {SITE.legalUpdated}</p>}>
      <p>{SITE.product} is a product of {SITE.company} ("we", "us"). This policy explains what we collect when you use {SITE.product}, why, and what you can do about it. We collect as little as we can to run the service.</p>

      <h2>What we collect</h2>
      <ul>
        <li><strong>Your account:</strong> your username and your password. Passwords are stored only as a one-way hash (bcrypt); we never see or store the password itself.</li>
        <li><strong>Your learning activity:</strong> which steps and tasks you have done, your check results, your answers to questions, XP, streaks, levels, the goal you pick at sign up and your time zone (so a streak day matches your day).</li>
        <li><strong>If you sign in with Google or GitHub:</strong> we receive your name, your email address (only if they have verified it) and an account number, nothing else. We use the email to keep your account recoverable and never post anything anywhere on your behalf.</li>
        <li><strong>Your certificates:</strong> when you claim a certificate for a lab you finished, the full name you type, the lab, the date and your task count appear on a public page that anyone with its link can open (that is what makes it shareable on LinkedIn or X). You can hide any certificate on its page at any time.</li>
        <li><strong>Your lab files:</strong> the files in your lab workspace and the output of what you run in your lab machine.</li>
        <li><strong>Technical data:</strong> our servers keep standard logs of requests, which include your IP address, the time and the page or action requested. We use them to keep the service running and secure.</li>
        <li><strong>Your browser:</strong> we keep your login token and small preferences (theme, panel sizes) in your browser's local storage. The Preview tab uses one cookie that only works for previewing your own lab app.</li>
      </ul>

      <h2>What we do not do</h2>
      <ul>
        <li>We do not sell your data or share it for advertising.</li>
        <li>The AI tutor, design reviews and the AI labs send your question and the code they need to OpenAI, through our own gateway, to get an answer. OpenAI receives no name or email address with it.</li>
        <li>We do not use third party analytics or tracking scripts. Fonts and images are served from our own servers.</li>
      </ul>

      <h2>How we use it</h2>
      <p>To run your labs, check your work, save your progress, show your XP and streaks, keep the service secure, and fix problems.</p>

      <h2>How we protect it</h2>
      <p>Each lab runs in its own isolated container with limits on memory and processes, and without internet access unless a lab needs it. Passwords are hashed. Access to our servers is restricted.</p>

      <h2>How long we keep it</h2>
      <p>We keep your account, progress and lab files for as long as your account exists. Lab machines are stopped when you are away; your files are kept so you can carry on. Server logs are kept only as long as we need them to run and secure the service.</p>

      <h2>Your choices</h2>
      <p>You can ask us for a copy of your data, to correct it, or to delete your account and everything linked to it. Write to {mail} from the account you want to change and we will reply.</p>

      <h2>Children</h2>
      <p>If you are under 18, please use {SITE.product} with the permission of a parent or guardian.</p>

      <h2>Changes</h2>
      <p>If we change this policy we will update the date at the top, and tell you in the app if the change is important.</p>

      <h2>Contact</h2>
      <p>Questions about privacy: {mail}.</p>
    </InfoLayout>
  );
}

export function TermsPage() {
  return (
    <InfoLayout title="Terms of Service" intro={<p className="muted">Last updated {SITE.legalUpdated}</p>}>
      <p>{SITE.product} is a product of {SITE.company} ("we", "us"). These terms are the agreement between you and {SITE.company} when you use {SITE.product}. By creating an account or using the service you agree to them.</p>

      <h2>Your account</h2>
      <ul>
        <li>Keep your password to yourself. You are responsible for what happens under your account.</li>
        <li>One account per person, please.</li>
      </ul>

      <h2>Using the labs fairly</h2>
      <p>Your lab machine is for learning. You must not:</p>
      <ul>
        <li>try to break out of your lab machine, reach other users' machines, or attack our servers or anyone else's;</li>
        <li>use lab machines for crypto mining, sending spam, scanning networks or anything illegal;</li>
        <li>overload the service on purpose, or get around the limits on machines;</li>
        <li>copy our lessons, tests or solutions in bulk, or publish them as your own.</li>
      </ul>
      <p>We may stop a machine or suspend an account that breaks these rules.</p>

      <h2>Your code</h2>
      <p>The code you write is yours. You let us store it and run it so we can provide the service (for example, to run your checks).</p>

      <h2>Our content</h2>
      <p>The lessons, labs, tests and everything else we provide belong to {SITE.company}. You may use them for your own learning.</p>

      <h2>Lab machines</h2>
      <p>Machines have limits on memory, processor time and processes. They stop when idle and can be reset. Do not keep anything important only in a lab machine.</p>

      <h2>Early access</h2>
      <p>{SITE.product} is in early access. Features may change, and the service may sometimes be unavailable. We provide it as it is, without guarantees, and to the extent the law allows we are not liable for indirect losses or lost data.</p>

      <h2>Ending your account</h2>
      <p>You can stop using {SITE.product} at any time and ask us to delete your account. We may close accounts that break these terms.</p>

      <h2>Changes</h2>
      <p>We may update these terms. We will change the date at the top and tell you in the app if the change is important. If you keep using the service after that, you accept the new terms.</p>

      <h2>Contact</h2>
      <p>Questions about these terms: {mail}.</p>
    </InfoLayout>
  );
}
