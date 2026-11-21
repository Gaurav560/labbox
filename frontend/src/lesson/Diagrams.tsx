import type { ReactNode } from "react";
import { Svg } from "./PicturePrimitives";

/*
 * Built-in pictures for ideas you cannot see (Content standard: "pictures for invisible ideas").
 * A chapter asks for one with :::diagram{name="shared-list"}, and the text inside becomes the caption.
 * Drawn as SVG with theme colours (CSS variables), so they work in light and dark themes and stay sharp
 * at any text size.
 */

type BoxTone = "plain" | "accent" | "copy" | "highlight";

interface BoxProps {
  x: number;
  y: number;
  w: number;
  h: number;
  label: string;
  tone?: BoxTone;
  code?: boolean;
}

function Box({ x, y, w, h, label, tone = "plain", code }: BoxProps) {
  return (
    <g className={`dg-box dg-${tone}`}>
      <rect x={x} y={y} width={w} height={h} rx={8} />
      <text className={code ? "dg-code" : undefined} x={x + w / 2} y={y + h / 2 + 5} textAnchor="middle">{label}</text>
    </g>
  );
}

function Arrow({ x1, y1, x2, y2 }: { x1: number; y1: number; x2: number; y2: number }) {
  return <line className="dg-arrow" x1={x1} y1={y1} x2={x2} y2={y2} markerEnd="var(--figure-arrowhead)" />;
}

function Cells({ x, y, values, tone = "plain" }: { x: number; y: number; values: (string | number)[]; tone?: BoxTone }) {
  return (
    <g>
      {values.map((v, i) => (
        <Box key={i} x={x + i * 46} y={y} w={42} h={38} label={String(v)} tone={tone} code />
      ))}
    </g>
  );
}

/** Two names, one list: b = a shares the list; a.copy() makes a second one. */
function SharedList() {
  return (
    <Svg viewBox="0 0 440 206" label="a and b point to the same list [3, 1, 2]; c points to a separate copy">
      <text className="dg-note dg-code" x={10} y={22}>b = a</text>
      <Box x={10} y={40} w={56} h={34} label="a" tone="accent" code />
      <Box x={10} y={92} w={56} h={34} label="b" tone="accent" code />
      <Arrow x1={68} y1={57} x2={196} y2={80} />
      <Arrow x1={68} y1={109} x2={196} y2={90} />
      <Cells x={200} y={66} values={[3, 1, 2]} />
      <text className="dg-note" x={200} y={56}>one list</text>
      <text className="dg-note dg-code" x={10} y={164}>c = a.copy()</text>
      <Box x={10} y={170} w={56} h={26} label="c" tone="accent" code />
      <Arrow x1={68} y1={183} x2={196} y2={183} />
      <Cells x={200} y={164} values={[3, 1, 2]} tone="copy" />
      <text className="dg-note" x={344} y={188}>its own list</text>
    </Svg>
  );
}

/** The mutable default: every call without a basket points at the one list made by the def line. */
function DefaultList() {
  return (
    <Svg viewBox="0 0 440 190" label="Three calls to add_item all point to the same default list, which keeps growing">
      <g className="dg-cells-small">
        <Box x={10} y={14} w={150} h={34} label='add_item("milk")' tone="accent" code />
        <Box x={10} y={74} w={150} h={34} label='add_item("bread")' tone="accent" code />
        <Box x={10} y={134} w={150} h={34} label='add_item("eggs")' tone="accent" code />
      </g>
      <Arrow x1={162} y1={31} x2={238} y2={84} />
      <Arrow x1={162} y1={91} x2={238} y2={91} />
      <Arrow x1={162} y1={151} x2={238} y2={98} />
      <text className="dg-note" x={242} y={66}><tspan className="dg-code">basket=[]</tspan> (made once)</text>
      <g className="dg-cells-small">
        <Box x={242} y={74} w={60} h={34} label="milk" />
        <Box x={306} y={74} w={64} h={34} label="bread" />
        <Box x={374} y={74} w={58} h={34} label="eggs" />
      </g>
      <text className="dg-note" x={242} y={130}>one list,</text>
      <text className="dg-note" x={242} y={146}>shared by every call</text>
    </Svg>
  );
}

/** Go slices: two slice headers viewing one array; slices.Clone gets its own array. */
function SliceArray() {
  return (
    <Svg viewBox="0 0 440 200" label="Slices a and b view the same array; c, made with slices.Clone, has its own array">
      <Box x={10} y={30} w={90} h={34} label="a  len 3" tone="accent" />
      <Box x={10} y={84} w={90} h={34} label="b  len 3" tone="accent" />
      <Arrow x1={102} y1={47} x2={196} y2={68} />
      <Arrow x1={102} y1={101} x2={196} y2={80} />
      <text className="dg-note" x={200} y={50}>one array</text>
      <Cells x={200} y={56} values={[3, 1, 2]} />
      <text className="dg-note dg-code" x={10} y={150}>c := slices.Clone(a)</text>
      <Box x={10} y={158} w={90} h={34} label="c  len 3" tone="accent" />
      <Arrow x1={102} y1={175} x2={196} y2={175} />
      <Cells x={200} y={156} values={[3, 1, 2]} tone="copy" />
      <text className="dg-note" x={344} y={180}>its own array</text>
    </Svg>
  );
}

/** Go errors: each %w adds a layer of context around the original error. */
function ErrorChain() {
  return (
    <Svg viewBox="0 0 440 170" label="An error wrapped twice: transfer, then withdraw 250 from 100, around ErrInsufficientFunds">
      <g className="dg-box"><rect x={10} y={10} width={420} height={150} rx={12} /></g>
      <text className="dg-note dg-code" x={24} y={34}>fmt.Errorf("transfer: %w", err)</text>
      <g className="dg-box dg-accent"><rect x={30} y={46} width={380} height={100} rx={10} /></g>
      <text className="dg-note dg-code" x={44} y={70}>fmt.Errorf("withdraw 250 from 100: %w", ...)</text>
      <Box x={70} y={86} w={300} h={42} label="ErrInsufficientFunds" tone="highlight" code />
    </Svg>
  );
}

/** Go receivers: a value receiver changes a copy; a pointer receiver changes the caller's value. */
function ValueVsPointer() {
  return (
    <Svg viewBox="0 0 440 190" label="With a value receiver the copy becomes 150 and the wallet stays 100; with a pointer receiver the wallet becomes 150">
      <text className="dg-note dg-code" x={10} y={20}>func (w Wallet) Deposit(50)</text>
      <Box x={10} y={30} w={130} h={36} label="wallet: 100" tone="accent" />
      <Arrow x1={142} y1={48} x2={220} y2={48} />
      <Box x={224} y={30} w={130} h={36} label="copy: 150" />
      <text className="dg-note" x={360} y={53}>thrown away</text>
      <text className="dg-note dg-code" x={10} y={112}>func (w *Wallet) Deposit(50)</text>
      <Box x={10} y={122} w={130} h={36} label="wallet: 150" tone="accent" />
      <Box x={224} y={122} w={130} h={36} label="w (a pointer)" />
      <Arrow x1={222} y1={140} x2={144} y2={140} />
      <text className="dg-note" x={224} y={176}>changes the real wallet</text>
    </Svg>
  );
}

/** Goroutines: five 200 ms waits one after another versus side by side. */
function Goroutines() {
  const bars = [0, 1, 2, 3, 4];
  return (
    <Svg viewBox="0 0 440 230" label="One after another, five waits take 1000 ms; as goroutines they overlap and take about 200 ms">
      <text className="dg-note" x={10} y={18}>one after another: 1000 ms</text>
      {bars.map((i) => (
        <g key={`s${i}`} className="dg-box"><rect x={10 + i * 80} y={26} width={76} height={18} rx={4} /></g>
      ))}
      <text className="dg-note" x={10} y={78}>goroutines, side by side: about 200 ms</text>
      {bars.map((i) => (
        <g key={`g${i}`} className="dg-box dg-accent"><rect x={10} y={86 + i * 26} width={76} height={18} rx={4} /></g>
      ))}
      <line className="dg-arrow" x1={90} y1={86} x2={90} y2={208} strokeDasharray="4 4" />
      <text className="dg-note" x={96} y={150}><tspan className="dg-code">wg.Wait()</tspan> returns here</text>
    </Svg>
  );
}

/** Java strings: == compares addresses, equals compares the letters. */
function StringEquals() {
  return (
    <Svg viewBox="0 0 440 200" label="a and b point to two different String objects that both hold tea; a == b is false, a.equals(b) is true">
      <Box x={10} y={30} w={60} h={34} label="a" tone="accent" code />
      <Box x={10} y={110} w={60} h={34} label="b" tone="accent" code />
      <Arrow x1={72} y1={47} x2={196} y2={47} />
      <Arrow x1={72} y1={127} x2={196} y2={127} />
      <Box x={200} y={28} w={110} h={38} label='"tea"' code />
      <Box x={200} y={108} w={110} h={38} label='"tea"' code />
      <text className="dg-note" x={320} y={52}>object 1</text>
      <text className="dg-note" x={320} y={132}>object 2</text>
      <text className="dg-note" x={10} y={180}><tspan className="dg-code">a == b</tspan> is false (two objects)</text>
      <text className="dg-note" x={10} y={196}><tspan className="dg-code">a.equals(b)</tspan> is true (same letters)</text>
    </Svg>
  );
}

/** Java objects: a variable holds the address of an object, so b = a shares one object. */
function ObjectReference() {
  return (
    <Svg viewBox="0 0 440 190" label="Variables a and b both hold the address of one BankAccount object with balance 150">
      <text className="dg-note dg-code" x={10} y={20}>BankAccount b = a;</text>
      <Box x={10} y={36} w={70} h={34} label="a" tone="accent" code />
      <Box x={10} y={100} w={70} h={34} label="b" tone="accent" code />
      <Arrow x1={82} y1={53} x2={226} y2={76} />
      <Arrow x1={82} y1={117} x2={226} y2={94} />
      <g className="dg-box"><rect x={230} y={50} width={190} height={70} rx={10} /></g>
      <text className="dg-note dg-code" x={244} y={76}>BankAccount</text>
      <text className="dg-note" x={244} y={100}>owner: Riya, balance: 150</text>
      <text className="dg-note" x={10} y={172}><tspan className="dg-code">b.deposit(50)</tspan> changes the one object a also sees</text>
    </Svg>
  );
}

/** Redis: one shared dictionary in memory, used by every outlet and worker; the database stays on disk. */
function RedisShared() {
  return (
    <Svg viewBox="0 0 440 200" label="Three apps, two outlets and a worker, all talk to one Redis server that keeps data in memory; Postgres keeps the full records on disk">
      <Box x={10} y={14} w={118} h={34} label="outlet app" />
      <Box x={10} y={82} w={118} h={34} label="outlet app" />
      <Box x={10} y={150} w={118} h={34} label="worker" />
      <Arrow x1={130} y1={31} x2={232} y2={86} />
      <Arrow x1={130} y1={99} x2={232} y2={99} />
      <Arrow x1={130} y1={167} x2={232} y2={112} />
      <Box x={236} y={74} w={110} h={50} label="Redis" tone="accent" />
      <text className="dg-note" x={236} y={66}>in memory, shared</text>
      <text className="dg-note" x={236} y={142}>reads and writes</text>
      <text className="dg-note" x={236} y={158}>under 1 ms</text>
      <Box x={356} y={150} w={78} h={34} label="Postgres" />
      <text className="dg-note" x={356} y={142}>on disk</text>
    </Svg>
  );
}

/** Round trips: 2000 commands one by one wait 2000 times; a pipeline waits once. */
function RoundTrips() {
  return (
    <Svg viewBox="0 0 440 210" label="Without a pipeline every command waits for its own answer, about 0.5 ms each; with a pipeline all commands go together and the answers come back together">
      <text className="dg-note" x={10} y={18}>one at a time: wait, wait, wait</text>
      <Box x={10} y={28} w={70} h={30} label="app" />
      <Box x={360} y={28} w={70} h={30} label="Redis" tone="accent" />
      {[0, 1, 2].map((i) => (
        <g key={i}>
          <Arrow x1={84} y1={66 + i * 18} x2={356} y2={66 + i * 18} />
        </g>
      ))}
      <text className="dg-note" x={150} y={128}>2000 trips x 0.5 ms = about 1 s</text>
      <text className="dg-note" x={10} y={156}>pipeline: send all, then read all</text>
      <Box x={10} y={166} w={70} h={30} label="app" />
      <Box x={360} y={166} w={70} h={30} label="Redis" tone="accent" />
      <Arrow x1={84} y1={181} x2={356} y2={181} />
      <text className="dg-note" x={150} y={204}>1 trip, a few ms</text>
    </Svg>
  );
}

/** Cache-aside: ask Redis first; on a miss, ask the slow system and keep the answer with a TTL. */
function CacheAside() {
  return (
    <Svg viewBox="0 0 440 210" label="The app asks Redis first. On a hit it answers at once. On a miss it asks the slow billing system, stores the answer in Redis with a TTL, then answers">
      <Box x={10} y={84} w={84} h={40} label="app" />
      <Arrow x1={96} y1={96} x2={196} y2={44} />
      <Box x={200} y={22} w={110} h={40} label="Redis" tone="accent" />
      <text className="dg-note" x={318} y={36}>1. hit?</text>
      <text className="dg-note" x={318} y={52}>answer at once</text>
      <Arrow x1={96} y1={112} x2={196} y2={166} />
      <Box x={200} y={148} w={110} h={40} label="billing" />
      <text className="dg-note" x={318} y={162}>2. miss: slow,</text>
      <text className="dg-note" x={318} y={178}>1.5 s</text>
      <Arrow x1={255} y1={146} x2={255} y2={66} />
      <text className="dg-note" x={262} y={110}>3. store with TTL</text>
    </Svg>
  );
}

/** Streams: one log, a consumer group shares entries out; unacknowledged work waits in the pending list. */
function ConsumerGroup() {
  return (
    <Svg viewBox="0 0 440 212" label="A stream of entries feeds a consumer group; each entry goes to one worker; entries stay in the pending list until the worker acknowledges them">
      <text className="dg-note" x={10} y={18}>stream: an append-only log</text>
      <Cells x={10} y={26} values={["1-0", "2-0", "3-0", "4-0"]} />
      <Arrow x1={110} y1={70} x2={150} y2={96} />
      <Box x={120} y={98} w={140} h={34} label="group: kitchen" tone="accent" />
      <Arrow x1={160} y1={134} x2={80} y2={164} />
      <Arrow x1={220} y1={134} x2={300} y2={164} />
      <Box x={10} y={166} w={120} h={34} label="barista1" />
      <Box x={250} y={166} w={120} h={34} label="barista2" />
      <text className="dg-note" x={276} y={110}>pending until XACK:</text>
      <text className="dg-note" x={276} y={126}>a crash loses nothing</text>
    </Svg>
  );
}

/** Persistence: RDB snapshots now and then; AOF logs every write. What a crash at the end loses. */
function Persistence() {
  return (
    <Svg viewBox="0 0 440 200" label="On a time line, RDB takes a snapshot every few minutes, so a crash loses the writes since the last one; AOF logs every write, so a crash loses at most about one second">
      <text className="dg-note" x={10} y={18}>RDB: a snapshot now and then</text>
      <line className="dg-arrow" x1={10} y1={50} x2={400} y2={50} />
      <Box x={40} y={34} w={70} h={32} label="snap" tone="accent" />
      <Box x={200} y={34} w={70} h={32} label="snap" tone="accent" />
      <Box x={290} y={34} w={110} h={32} label="lost writes" tone="highlight" />
      <text className="dg-note" x={404} y={30}>crash</text>
      <text className="dg-note" x={10} y={110}>AOF: every write logged</text>
      <line className="dg-arrow" x1={10} y1={142} x2={400} y2={142} />
      {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].map((i) => (
        <Box key={i} x={20 + i * 30} y={128} w={24} h={28} label="w" tone="accent" />
      ))}
      <Box x={384} y={128} w={20} h={28} label="" tone="highlight" />
      <text className="dg-note" x={150} y={186}>a crash loses at most about one second</text>
    </Svg>
  );
}

/** Replication: the primary takes writes and streams them to read-only replicas, a little behind. */
function Replication() {
  return (
    <Svg viewBox="0 0 440 200" label="Apps write to the primary; the primary sends every write to two replicas, which apps can read from; the replicas can be a few milliseconds behind">
      <Box x={10} y={80} w={90} h={36} label="apps" />
      <Arrow x1={102} y1={98} x2={170} y2={98} />
      <text className="dg-note" x={108} y={88}>writes</text>
      <Box x={174} y={78} w={110} h={40} label="primary" tone="accent" />
      <Arrow x1={286} y1={88} x2={330} y2={46} />
      <Arrow x1={286} y1={108} x2={330} y2={150} />
      <Box x={334} y={24} w={100} h={36} label="replica" />
      <Box x={334} y={138} w={100} h={36} label="replica" />
      <text className="dg-note" x={300} y={92}>every write,</text>
      <text className="dg-note" x={300} y={108}>a few ms later</text>
      <text className="dg-note" x={334} y={190}>read-only copies</text>
    </Svg>
  );
}

/** A library is called by your code; a framework calls your code (inversion of control). */
function LibraryVsFramework() {
  return (
    <Svg viewBox="0 0 440 210" label="With a library, your code is in charge and calls the library. With a framework, the framework is in charge and calls your code when something happens, such as a request arriving">
      <text className="dg-note" x={10} y={18}>a library: you call it</text>
      <Box x={10} y={28} w={150} h={36} label="your code" tone="accent" />
      <Arrow x1={162} y1={46} x2={272} y2={46} />
      <text className="dg-note" x={176} y={38}>calls</text>
      <Box x={276} y={28} w={150} h={36} label="library (Jackson)" />
      <text className="dg-note" x={10} y={118}>a framework: it calls you</text>
      <Box x={10} y={128} w={150} h={36} label="Spring" />
      <Arrow x1={162} y1={146} x2={272} y2={146} />
      <text className="dg-note" x={166} y={138}>request arrives,</text>
      <text className="dg-note" x={166} y={180}>calls your method</text>
      <Box x={276} y={128} w={150} h={36} label="your controller" tone="accent" />
    </Svg>
  );
}

/** What a web backend has to do, and which parts Spring Boot does for you. */
function BackendStack() {
  const rows: [string, boolean][] = [
    ["your endpoints and rules", true],
    ["turn JSON into objects and back", false],
    ["route URLs to methods", false],
    ["handle many requests at once (threads)", false],
    ["read HTTP from the network", false],
    ["open a port and accept connections", false],
  ];
  return (
    <Svg viewBox="0 0 440 236" label="A stack of six jobs every web backend needs. You write only the top one, your endpoints and rules; Spring Boot and its embedded Tomcat server do the five below">
      {rows.map(([label, yours], i) => (
        <Box key={label} x={10} y={8 + i * 36} w={300} h={30} label={label} tone={yours ? "accent" : "plain"} />
      ))}
      <text className="dg-note" x={320} y={28}>you write</text>
      <text className="dg-note" x={320} y={120}>Spring Boot</text>
      <text className="dg-note" x={320} y={136}>does these</text>
      <line className="dg-arrow" x1={316} y1={48} x2={316} y2={222} />
    </Svg>
  );
}

/** The history of Spring as a timeline. */
function SpringTimeline() {
  const events: [number, string, string][] = [
    [2002, "Rod Johnson's book", "simpler Java is possible"],
    [2004, "Spring 1.0", "plain objects, injection"],
    [2014, "Spring Boot 1.0", "just run it, no XML"],
    [2018, "Spring Boot 2", "reactive web, Java 8+"],
    [2022, "Spring Boot 3", "Java 17, Jakarta EE"],
  ];
  return (
    <Svg viewBox="0 0 440 226" label="A timeline: 2002 Rod Johnson's book, 2004 Spring 1.0, 2014 Spring Boot 1.0, 2018 Spring Boot 2, 2022 Spring Boot 3">
      <line className="dg-arrow" x1={30} y1={24} x2={30} y2={212} />
      {events.map(([year, what, why], i) => (
        <g key={year}>
          <Box x={46} y={8 + i * 42} w={60} h={30} label={String(year)} tone="accent" code />
          <text className="dg-label" x={118} y={21 + i * 42}>{what}</text>
          <text className="dg-note" x={118} y={36 + i * 42}>{why}</text>
        </g>
      ))}
    </Svg>
  );
}

/** What SpringApplication.run does, in order. */
function StartupSequence() {
  const steps = [
    "1. read application.properties",
    "2. scan com.shop for @Component classes",
    "3. auto-configure (web, JSON, ...)",
    "4. create the beans, inject them",
    "5. start Tomcat on port 8080",
    "6. Started: ready for requests",
  ];
  return (
    <Svg viewBox="0 0 440 236" label="SpringApplication.run reads application.properties, scans the package for components, applies auto-configuration, creates and injects the beans, starts Tomcat on port 8080, and is then ready for requests">
      <Box x={10} y={8} w={420} h={30} label="SpringApplication.run(...)" tone="accent" code />
      {steps.map((s, i) => (
        <g key={s}>
          <Box x={30} y={46 + i * 31} w={380} h={26} label={s} />
        </g>
      ))}
    </Svg>
  );
}

/** The container creates each bean once and passes it to the constructors that ask for it. */
function DiContainer() {
  return (
    <Svg viewBox="0 0 440 210" label="The Spring container creates one VisitCounter and one PriceCalculator, then passes the same VisitCounter to HomeController and StatsController through their constructors">
      <g className="dg-box"><rect x={6} y={6} width={428} height={196} rx={12} /></g>
      <text className="dg-note" x={18} y={26}>the Spring container (application context)</text>
      <Box x={20} y={44} w={150} h={34} label="VisitCounter" tone="accent" code />
      <Box x={20} y={140} w={150} h={34} label="PriceCalculator" tone="accent" code />
      <Arrow x1={172} y1={55} x2={262} y2={44} />
      <Arrow x1={172} y1={67} x2={262} y2={96} />
      <Arrow x1={172} y1={157} x2={262} y2={157} />
      <Box x={266} y={28} w={156} h={30} label="HomeController" code />
      <Box x={266} y={82} w={156} h={30} label="StatsController" code />
      <Box x={266} y={142} w={156} h={30} label="PriceController" code />
      <text className="dg-note" x={20} y={104}>one object each,</text>
      <text className="dg-note" x={20} y={120}>passed to constructors</text>
    </Svg>
  );
}

/** Controller, service, repository: each layer calls only the one below it. */
function Layers() {
  const rows: [string, string][] = [
    ["ProductController", "HTTP: paths, status codes, JSON"],
    ["ProductService", "the rules: averages, budgets, checks"],
    ["ProductRepository", "the data: find, save, delete"],
  ];
  return (
    <Svg viewBox="0 0 440 200" label="Three layers: the controller handles HTTP and calls the service, the service holds the rules and calls the repository, and the repository reads and writes the data">
      {rows.map(([name, job], i) => (
        <g key={name}>
          <Box x={10} y={10 + i * 62} w={170} h={36} label={name} tone={i === 1 ? "accent" : "plain"} code />
          <text className="dg-note" x={192} y={33 + i * 62}>{job}</text>
          {i < 2 && <Arrow x1={95} y1={48 + i * 62} x2={95} y2={70 + i * 62} />}
        </g>
      ))}
      <text className="dg-note" x={10} y={196}>each layer calls only the one below it</text>
    </Svg>
  );
}

/** How the parts of a URL become method parameters. */
function RequestMapping() {
  return (
    <Svg viewBox="0 0 440 200" label="In GET /products/3?sort=price, the 3 in the path goes to the @PathVariable id parameter, and sort=price in the query goes to the @RequestParam sort parameter">
      <Box x={10} y={14} w={420} h={36} label="GET /products/3?sort=price" tone="accent" code />
      <Arrow x1={140} y1={52} x2={110} y2={120} />
      <Arrow x1={300} y1={52} x2={330} y2={120} />
      <text className="dg-note" x={64} y={92}>the path part</text>
      <text className="dg-note" x={300} y={92}>the query part</text>
      <Box x={10} y={124} w={200} h={34} label="@PathVariable id" code />
      <Box x={230} y={124} w={200} h={34} label="@RequestParam sort" code />
      <text className="dg-note" x={60} y={180}>id = 3</text>
      <text className="dg-note" x={290} y={180}>sort = "price"</text>
    </Svg>
  );
}

const DIAGRAMS: Record<string, () => JSX.Element> = {
  "library-vs-framework": LibraryVsFramework,
  "backend-stack": BackendStack,
  "spring-timeline": SpringTimeline,
  "startup-sequence": StartupSequence,
  "di-container": DiContainer,
  layers: Layers,
  "request-mapping": RequestMapping,
  "consumer-group": ConsumerGroup,
  persistence: Persistence,
  replication: Replication,
  "redis-shared": RedisShared,
  "round-trips": RoundTrips,
  "cache-aside": CacheAside,
  "string-equals": StringEquals,
  "object-reference": ObjectReference,
  "shared-list": SharedList,
  "default-list": DefaultList,
  "slice-array": SliceArray,
  "error-chain": ErrorChain,
  "value-vs-pointer": ValueVsPointer,
  goroutines: Goroutines,
};

export default function Diagram({ name, caption }: { name: string; caption?: ReactNode }) {
  const Picture = DIAGRAMS[name];
  if (!Picture) return null;
  return (
    <figure className="diagram">
      <Picture />
      {caption && <figcaption>{caption}</figcaption>}
    </figure>
  );
}
