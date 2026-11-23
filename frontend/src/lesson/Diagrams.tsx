import type { ReactNode } from "react";
import { Svg } from "./PicturePrimitives";
import { SketchNested, SketchSteps } from "./Sketch";

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
        <Box x={10} y={14} w={150} h={34} label='add_item("mint")' tone="accent" code />
        <Box x={10} y={74} w={150} h={34} label='add_item("bread")' tone="accent" code />
        <Box x={10} y={134} w={150} h={34} label='add_item("eggs")' tone="accent" code />
      </g>
      <Arrow x1={162} y1={31} x2={238} y2={84} />
      <Arrow x1={162} y1={91} x2={238} y2={91} />
      <Arrow x1={162} y1={151} x2={238} y2={98} />
      <text className="dg-note" x={242} y={66}><tspan className="dg-code">basket=[]</tspan> (made once)</text>
      <g className="dg-cells-small">
        <Box x={242} y={74} w={60} h={34} label="mint" />
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
    <Svg viewBox="0 0 440 200" label="a and b point to two different String objects that both hold riya; a == b is false, a.equals(b) is true">
      <Box x={10} y={30} w={60} h={34} label="a" tone="accent" code />
      <Box x={10} y={110} w={60} h={34} label="b" tone="accent" code />
      <Arrow x1={72} y1={47} x2={196} y2={47} />
      <Arrow x1={72} y1={127} x2={196} y2={127} />
      <Box x={200} y={28} w={110} h={38} label='"riya"' code />
      <Box x={200} y={108} w={110} h={38} label='"riya"' code />
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

/** Redis: one shared dictionary in memory, used by every store app and worker; the database stays on disk. */
function RedisShared() {
  return (
    <Svg viewBox="0 0 440 200" label="Three programs, the two store apps and a worker, all talk to one Redis server that keeps data in memory; Postgres keeps the full records on disk">
      <Box x={10} y={14} w={118} h={34} label="Kothrud app" />
      <Box x={10} y={82} w={118} h={34} label="Baner app" />
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
    <Svg viewBox="0 0 440 210" label="The app asks Redis first. On a hit it answers at once. On a miss it asks the slow catalogue, stores the answer in Redis with a TTL, then answers">
      <Box x={10} y={84} w={84} h={40} label="app" />
      <Arrow x1={96} y1={96} x2={196} y2={44} />
      <Box x={200} y={22} w={110} h={40} label="Redis" tone="accent" />
      <text className="dg-note" x={318} y={36}>1. hit?</text>
      <text className="dg-note" x={318} y={52}>answer at once</text>
      <Arrow x1={96} y1={112} x2={196} y2={166} />
      <Box x={200} y={148} w={110} h={40} label="catalogue" />
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
      <Box x={120} y={98} w={140} h={34} label="group: packing" tone="accent" />
      <Arrow x1={160} y1={134} x2={80} y2={164} />
      <Arrow x1={220} y1={134} x2={300} y2={164} />
      <Box x={10} y={166} w={120} h={34} label="packer1" />
      <Box x={250} y={166} w={120} h={34} label="packer2" />
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
  // Hand-drawn and played step by step (the owner's sample for the Excalidraw look, 21 November).
  return (
    <SketchSteps
      title="SpringApplication.run(...)"
      intro="Press Play to watch the app start, one step at a time."
      label="SpringApplication.run reads application.properties, scans the package for components, applies auto-configuration, creates and injects the beans, starts Tomcat on port 8080, and is then ready for requests"
      steps={[
        { label: "1. read application.properties", says: "Spring reads your settings first: application.properties, then anything given on the command line. spring.application.name=shop-api is read here." },
        { label: "2. scan com.shop for components", says: "It looks through com.shop and every package under it for classes marked @Component, @Service or @RestController. A class outside com.shop is never found." },
        { label: "3. auto-configure (web, JSON, ...)", says: "It sees spring-boot-starter-web in your pom.xml, so it sets up a web server, JSON conversion (Jackson) and the part that sends each request to a controller." },
        { label: "4. create the beans, inject them", says: "It creates one object (a bean) for every class it found, and passes beans into the constructors that ask for them." },
        { label: "5. start Tomcat on port 8080", says: "It starts the embedded Tomcat web server inside your app. Nothing to install: the server is a library in your jar." },
        { label: "6. Started: ready for requests", says: "It logs \"Started ShopApiApplication in 0.9 seconds\" (about one second). Start-up is over; from now on the app only answers requests." },
      ]}
    />
  );
}

/** A singleton bean's life, played step by step. */
function BeanLifecycle() {
  return (
    <SketchSteps
      title="the life of a bean"
      intro="Press Play to follow one bean, PriceCatalog, from start-up to shutdown."
      label="Spring creates the bean with its constructor, passing its dependencies, then calls its @PostConstruct method; the bean then serves requests until shutdown, when Spring calls its @PreDestroy method"
      steps={[
        { label: "1. dependencies first", says: "Before creating PriceController, Spring creates what its constructor needs: here, PriceCatalog. Beans are created in dependency order." },
        { label: "2. constructor: new PriceCatalog(...)", says: "Spring calls the constructor, passing the beans it asks for. The object exists now, but nothing has prepared it yet." },
        { label: "3. @PostConstruct: load()", says: "Right after creating it, Spring calls the method marked @PostConstruct, once. Here it reads prices.csv into memory." },
        { label: "4. in use: serving requests", says: "The bean sits in the application context. Every request uses this same object, for as long as the app runs." },
        { label: "5. Ctrl+C: @PreDestroy", says: "When the app shuts down, Spring calls each bean's @PreDestroy method, so it can close files and connections cleanly." },
        { label: "6. gone", says: "The application context is closed, and the bean with it. Next start-up, everything happens again from step 1." },
      ]}
    />
  );
}

/** One request's journey through Spring MVC, played step by step. */
function RequestJourney() {
  return (
    <SketchSteps
      title="GET /api/v1/cart"
      intro="Press Play to follow one request from the network to your method and back."
      label="Tomcat receives the request and gives it a thread; the DispatcherServlet asks the handler mapping which method handles GET /api/v1/cart; Spring prepares the method's arguments; your method runs; Jackson writes the return value as JSON; Tomcat sends the response and the thread is free again"
      steps={[
        { label: "1. Tomcat: bytes in, a thread out", says: "Tomcat reads the request from the network and hands it to one of its worker threads (about 200 by default). Each request in progress has its own thread." },
        { label: "2. DispatcherServlet: the front desk", says: "Every request goes to the same place first: Spring's DispatcherServlet. It does not do the work itself; it finds who should." },
        { label: "3. handler mapping: which method?", says: "It looks up GET + /api/v1/cart in the table built at start-up, and finds CartController#cart(). No match for the path: 404. Path but not the method: 405." },
        { label: "4. arguments: fill the parameters", says: "Spring prepares each parameter of your method: path variables, query parameters, the JSON body read by Jackson. cart() has none, so this is quick." },
        { label: "5. your method runs", says: "Spring calls cart(). This is the only step you wrote. Everything around it is Spring." },
        { label: "6. converter: return value to JSON", says: "Your List comes back. A message converter (Jackson) writes it as JSON, after checking the client accepts JSON (the Accept header)." },
        { label: "7. response sent, thread free", says: "Tomcat sends 200 with the JSON body, and the thread goes back to the pool, ready for the next request." },
      ]}
    />
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

/** Jackson binds the JSON body to a record by field name, and writes the return value back as JSON. */
function JsonBinding() {
  return (
    <Svg viewBox="0 0 440 210" label="The JSON body name Vada pav, pricePaise 2500 is read by Jackson into a NewProduct record with the same field names; the method returns a Product, which Jackson writes back as JSON">
      <Box x={10} y={14} w={190} h={52} label='{"name": ...}' code />
      <text className="dg-note" x={10} y={84}>request body (JSON)</text>
      <Arrow x1={202} y1={40} x2={236} y2={40} />
      <text className="dg-note" x={204} y={30}>Jackson</text>
      <Box x={240} y={14} w={190} h={52} label="NewProduct record" tone="accent" code />
      <text className="dg-note" x={240} y={84}>method parameter</text>
      <Arrow x1={335} y1={92} x2={335} y2={120} />
      <Box x={240} y={124} w={190} h={40} label="Product (returned)" tone="accent" code />
      <Arrow x1={238} y1={144} x2={204} y2={144} />
      <text className="dg-note" x={206} y={136}>Jackson</text>
      <Box x={10} y={124} w={190} h={40} label='{"id": 4, ...}' code />
      <text className="dg-note" x={10} y={184}>response body (JSON)</text>
    </Svg>
  );
}

/** Any controller's exception goes to the one @RestControllerAdvice, which answers with a ProblemDetail. */
function ErrorFlow() {
  return (
    <Svg viewBox="0 0 440 210" label="The service throws ProductNotFoundException; it passes up through the controller to the RestControllerAdvice, whose ExceptionHandler builds a ProblemDetail with status 404, which is sent as JSON">
      <Box x={10} y={14} w={180} h={34} label="ProductService" code />
      <text className="dg-note" x={200} y={36}>throws ProductNotFoundException</text>
      <Arrow x1={100} y1={50} x2={100} y2={74} />
      <Box x={10} y={78} w={180} h={34} label="ProductController" code />
      <text className="dg-note" x={200} y={100}>does not catch it</text>
      <Arrow x1={100} y1={114} x2={100} y2={138} />
      <Box x={10} y={142} w={214} h={40} label="@RestControllerAdvice" tone="accent" code />
      <Arrow x1={226} y1={162} x2={246} y2={162} />
      <Box x={250} y={142} w={180} h={40} label="ProblemDetail, 404" tone="accent" code />
      <text className="dg-note" x={10} y={202}>sent as JSON, the same for every endpoint</text>
    </Svg>
  );
}

/** Profiles: application.yml first, then application-prod.yml on top; later values win. */
function ProfileLayers() {
  return (
    <Svg viewBox="0 0 440 200" label="application.yml sets shop.name to Shop API and free delivery to 50000; application-prod.yml, active with the prod profile, overrides both; the effective values are the prod ones">
      <text className="dg-note" x={10} y={18}>application.yml (always)</text>
      <Box x={10} y={26} w={250} h={30} label="shop.name: Shop API" code />
      <Box x={10} y={58} w={250} h={30} label="free-delivery...: 50000" code />
      <text className="dg-note" x={10} y={110}>application-prod.yml (prod profile)</text>
      <Box x={10} y={118} w={250} h={30} label="shop.name: ...(production)" tone="accent" code />
      <Box x={10} y={150} w={250} h={30} label="free-delivery...: 100000" tone="accent" code />
      <Arrow x1={264} y1={150} x2={300} y2={104} />
      <Box x={304} y={72} w={130} h={56} label="the app uses" tone="highlight" />
      <text className="dg-note" x={304} y={146}>the profile wins</text>
    </Svg>
  );
}

/** ORM: a class maps to a table, each field to a column, each object to a row. */
function OrmMapping() {
  return (
    <Svg viewBox="0 0 440 200" label="The Product entity class maps to the product table: id to the id primary key, name to name, pricePaise to price_paise; each Product object is one row">
      <text className="dg-note" x={10} y={18}>@Entity class Product</text>
      <Box x={10} y={26} w={170} h={30} label="Long id  (@Id)" code />
      <Box x={10} y={60} w={170} h={30} label="String name" code />
      <Box x={10} y={94} w={170} h={30} label="int pricePaise" code />
      {[41, 75, 109].map((y) => <Arrow key={y} x1={182} y1={y} x2={256} y2={y} />)}
      <text className="dg-note" x={260} y={18}>table product</text>
      <Box x={260} y={26} w={170} h={30} label="id  (primary key)" tone="accent" code />
      <Box x={260} y={60} w={170} h={30} label="name" tone="accent" code />
      <Box x={260} y={94} w={170} h={30} label="price_paise" tone="accent" code />
      <text className="dg-note" x={10} y={156}>one object = one row; Hibernate writes the SQL</text>
      <text className="dg-note" x={10} y={176}>camelCase fields become snake_case columns</text>
    </Svg>
  );
}

/** One-to-many: the foreign key lives in the order_item table. */
function OneToMany() {
  return (
    <Svg viewBox="0 0 440 200" label="The orders table has one row for order 1; the order_item table has two rows whose order_id column is 1, pointing back to it">
      <text className="dg-note" x={10} y={18}>orders</text>
      <Box x={10} y={26} w={150} h={30} label="id 1 | Asha" tone="accent" code />
      <text className="dg-note" x={210} y={18}>order_item</text>
      <Box x={210} y={26} w={220} h={30} label="kulfi x2 | order_id 1" code />
      <Box x={210} y={62} w={220} h={30} label="samosa x3 | order_id 1" code />
      <Arrow x1={208} y1={41} x2={162} y2={41} />
      <Arrow x1={208} y1={77} x2={162} y2={48} />
      <text className="dg-note" x={10} y={130}>@OneToMany(mappedBy = "order"): CustomerOrder.items</text>
      <text className="dg-note" x={10} y={150}>@ManyToOne + order_id: OrderItem.order</text>
      <text className="dg-note" x={10} y={176}>the foreign key is on the "many" side</text>
    </Svg>
  );
}

/** A transaction: every change commits together, or none does. */
function TransactionFlow() {
  return (
    <Svg viewBox="0 0 440 200" label="Inside one transaction, the kulfi stock goes from 10 to 8, then the samosa check fails; the transaction rolls back and the kulfi stock is 10 again">
      <Box x={10} y={10} w={420} h={30} label="@Transactional placeOrder(kulfi x2, samosa x5)" tone="accent" code />
      <Box x={30} y={50} w={180} h={30} label="kulfi: 10 -> 8" />
      <Arrow x1={212} y1={65} x2={240} y2={65} />
      <Box x={244} y={50} w={186} h={30} label="samosa: only 1 left!" tone="highlight" />
      <Arrow x1={337} y1={82} x2={337} y2={110} />
      <Box x={244} y={114} w={186} h={30} label="exception: roll back" tone="highlight" />
      <Arrow x1={242} y1={129} x2={212} y2={129} />
      <Box x={30} y={114} w={180} h={30} label="kulfi: back to 10" tone="accent" />
      <text className="dg-note" x={10} y={180}>all the changes commit together, or none of them do</text>
    </Svg>
  );
}

/** Flyway: versioned SQL files, applied once each, in order, recorded in flyway_schema_history. */
function FlywayVersions() {
  return (
    <Svg viewBox="0 0 440 200" label="Flyway applies V1, V2 and V3 in order, once each, and records each one in the flyway_schema_history table; on the next start it only runs files that are not recorded yet">
      {["V1__create_product.sql", "V2__add_category.sql", "V3__set_categories.sql"].map((f, i) => (
        <g key={f}>
          <Box x={10} y={14 + i * 44} w={220} h={32} label={f} code />
          <Arrow x1={232} y1={30 + i * 44} x2={262} y2={30 + i * 44} />
        </g>
      ))}
      <g className="dg-box"><rect x={266} y={10} width={164} height={132} rx={10} /></g>
      <text className="dg-note" x={276} y={30}>flyway_schema_history</text>
      {["1  success", "2  success", "3  success"].map((r, i) => <text key={r} className="dg-note dg-code" x={280} y={58 + i * 28}>{r}</text>)}
      <text className="dg-note" x={10} y={172}>each file runs once, in version order, on every database</text>
    </Svg>
  );
}

/** Test slices: @WebMvcTest starts the web layer with a mocked service; @DataJpaTest starts repositories and a database. */
function TestSlices() {
  return (
    <Svg viewBox="0 0 440 200" label="Two test slices side by side: @WebMvcTest starts the controller, with a mock in place of the service; @DataJpaTest starts the repository and an in-memory database, with nothing above it">
      <text className="dg-label" x={10} y={18}>@WebMvcTest</text>
      <Box x={10} y={28} w={190} h={32} label="controller (real)" tone="accent" />
      <Arrow x1={105} y1={62} x2={105} y2={86} />
      <Box x={10} y={90} w={190} h={32} label="service (a mock)" tone="highlight" />
      <text className="dg-note" x={10} y={146}>repository, database: not started</text>
      <text className="dg-label" x={240} y={18}>@DataJpaTest</text>
      <text className="dg-note" x={240} y={46}>controller, service: not started</text>
      <Box x={240} y={60} w={190} h={32} label="repository (real)" tone="accent" />
      <Arrow x1={335} y1={94} x2={335} y2={118} />
      <Box x={240} y={122} w={190} h={32} label="H2 database, in memory" tone="accent" />
      <text className="dg-note" x={10} y={184}>a slice starts one layer, so tests are fast and precise</text>
    </Svg>
  );
}

/** Actuator: health for the load balancer, info and metrics for people. */
function ActuatorEndpoints() {
  return (
    <Svg viewBox="0 0 440 200" label="A load balancer calls /actuator/health every few seconds and gets UP; a person or a dashboard reads /actuator/info and /actuator/metrics; all three are served by the Shop API">
      <Box x={10} y={20} w={130} h={34} label="load balancer" />
      <Box x={10} y={120} w={130} h={34} label="you, a dashboard" />
      <Arrow x1={142} y1={37} x2={246} y2={37} />
      <Arrow x1={142} y1={137} x2={246} y2={137} />
      <text className="dg-note" x={150} y={30}>every few seconds</text>
      <g className="dg-box"><rect x={250} y={10} width={180} height={160} rx={10} /></g>
      <text className="dg-label" x={264} y={30}>Shop API</text>
      <Box x={258} y={42} w={164} h={30} label="/actuator/health" tone="accent" code />
      <Box x={258} y={88} w={164} h={30} label="/actuator/info" code />
      <Box x={258} y={128} w={164} h={30} label="/actuator/metrics" code />
      <text className="dg-note" x={10} y={190}>health: UP or DOWN; info and metrics: facts and numbers</text>
    </Svg>
  );
}

/** The security filter chain: rules first, controller after. */
function SecurityChain() {
  return (
    <Svg viewBox="0 0 440 200" label="A request passes the security filters: first HTTP Basic reads who the caller is (401 if unknown), then the rules decide whether that caller may do this (403 if not); only then does the controller run">
      <Box x={10} y={20} w={90} h={34} label="request" />
      <Arrow x1={102} y1={37} x2={124} y2={37} />
      <Box x={128} y={20} w={140} h={34} label="who? (Basic)" tone="accent" />
      <Arrow x1={270} y1={37} x2={292} y2={37} />
      <Box x={296} y={20} w={134} h={34} label="allowed? (rules)" tone="accent" />
      <Arrow x1={363} y1={56} x2={363} y2={96} />
      <Box x={296} y={100} w={134} h={34} label="controller" />
      <Arrow x1={198} y1={56} x2={198} y2={96} />
      <Box x={128} y={100} w={140} h={34} label="401 Unauthorized" tone="highlight" />
      <text className="dg-note" x={310} y={160}>or 403 Forbidden</text>
      <text className="dg-note" x={10} y={186}>the first rule that matches the request decides</text>
    </Svg>
  );
}

/** Calling another service: the shop waits, and a timeout limits the wait. */
function ServiceCall() {
  return (
    <Svg viewBox="0 0 440 200" label="The client calls the Shop API, which calls the supplier with RestClient; with a 1 second read timeout, a slow supplier makes the shop answer 503 after one second instead of waiting">
      <Box x={10} y={30} w={100} h={34} label="client" />
      <Arrow x1={112} y1={47} x2={156} y2={47} />
      <Box x={160} y={30} w={120} h={34} label="Shop API" tone="accent" />
      <Arrow x1={282} y1={47} x2={326} y2={47} />
      <Box x={330} y={30} w={100} h={34} label="supplier" />
      <text className="dg-note dg-code" x={288} y={86}>RestClient</text>
      <Box x={160} y={110} w={270} h={32} label="no answer in 1 s: timeout" tone="highlight" />
      <Arrow x1={158} y1={126} x2={112} y2={126} />
      <Box x={10} y={110} w={100} h={32} label="503" tone="highlight" />
      <text className="dg-note" x={10} y={180}>fail fast, so one slow service cannot stall the shop</text>
    </Svg>
  );
}

/** The capstone checkout, from request to answer. */
function CheckoutFlow() {
  return (
    <Svg viewBox="0 0 440 200" label="POST /checkout is validated (400 if invalid), then CheckoutService runs in one transaction, taking stock and saving the order; out of stock rolls back and answers 409; success answers 201 with a Location">
      <Box x={10} y={14} w={130} h={32} label="POST /checkout" code />
      <Arrow x1={142} y1={30} x2={168} y2={30} />
      <Box x={172} y={14} w={100} h={32} label="@Valid" tone="accent" code />
      <Arrow x1={274} y1={30} x2={300} y2={30} />
      <Box x={304} y={14} w={126} h={32} label="400 problem" tone="highlight" />
      <Arrow x1={222} y1={48} x2={222} y2={70} />
      <Box x={16} y={74} w={410} h={34} label="@Transactional checkout: take stock, save order" tone="accent" />
      <Arrow x1={150} y1={110} x2={110} y2={136} />
      <Arrow x1={300} y1={110} x2={340} y2={136} />
      <Box x={10} y={140} w={190} h={32} label="201, Location /orders/1" />
      <Box x={240} y={140} w={190} h={32} label="409 problem, rollback" tone="highlight" />
      <text className="dg-note" x={10} y={194}>valid input, one transaction, a clear answer either way</text>
    </Svg>
  );
}

/** Python from zero, chapter 1: what really happens after "python3 first.py", played step by step. */
function PythonRunsAFile() {
  return (
    <SketchSteps
      title="python3 first.py"
      intro="Press Play to watch Python run your file, one step at a time."
      label="You type python3 first.py and press Enter; Python reads the whole file and checks its grammar, turns it into bytecode, runs the lines from the top one at a time, sends what print gives it to the terminal, and stops at the end of the file"
      steps={[
        { label: "1. you press Enter", says: "The terminal starts the program called python3 and hands it one thing: the name of your file, first.py." },
        { label: "2. read and check the grammar", says: "Python reads the whole file first and checks that every line is written correctly. One missing quote here and nothing runs at all: you get a SyntaxError." },
        { label: "3. translate to bytecode", says: "Python turns your lines into bytecode: small, simple instructions it can carry out quickly. You never see this step; it takes a few milliseconds." },
        { label: "4. run line 1, then line 2, ...", says: "Now it runs your program from the top, one line at a time, in order. Lines starting with # are notes for people, so they are skipped." },
        { label: "5. print sends text to the screen", says: "Each print(...) sends its text to the terminal, followed by a new line. That is the only reason you see anything." },
        { label: "6. end of the file: stop", says: "After the last line there is nothing left to do, so Python stops and the terminal shows its prompt again, ready for your next command." },
      ]}
    />
  );
}

/** Python from zero, chapter 3: one function call, from the call to the value coming back. */
function FunctionCall() {
  return (
    <SketchSteps
      title='message = greet("Asha")'
      intro="Press Play to follow one function call, from the call to the answer."
      label="Python evaluates greet with the argument Asha: it jumps into the function, the parameter name gets the value Asha, the body runs and builds the text, return hands the text back, and the caller stores it in message"
      steps={[
        { label: '1. the call: greet("Asha")', says: "Python reaches the right-hand side of the = sign first. It sees a name followed by brackets: that means call this function." },
        { label: "2. jump into the function", says: "Python remembers where it was, then jumps to the def greet line. Your program is now inside the function." },
        { label: '3. name = "Asha"', says: "The parameter name is given the value from the call. Inside the function, name means \"Asha\" for this call only." },
        { label: "4. the body runs", says: 'The indented lines run, top to bottom. Here one line builds the text f"Hello, {name}!", which becomes "Hello, Asha!".' },
        { label: "5. return hands the value back", says: "return ends the function at once and carries the value back to the spot where it was called. The function's own name variable is gone now." },
        { label: '6. message = "Hello, Asha!"', says: "Back where it started, Python finishes the line: the returned text is stored in message, and the program goes on to the next line." },
      ]}
    />
  );
}

/** Python from zero, chapter 6: how to read a traceback, from the bottom up. */
function TracebackBottomUp() {
  return (
    <SketchSteps
      title="reading a traceback"
      intro="Press Play to read a real traceback the way experienced developers do: from the bottom up."
      label="Read the last line first: the kind of error and its message. Then the frame just above it: the file, the line number and the code where it happened. Then walk up through the calls that led there, up to your program's own line"
      steps={[
        { label: "1. the last line: what went wrong", says: "ZeroDivisionError: division by zero. The kind of error, then a short message. Always read this line first." },
        { label: "2. the frame above: where", says: 'File "report.py", line 3, in average, and the code: sum(amounts) / len(amounts). The ~~~^~~~ marks show the exact division.' },
        { label: "3. one call up: who asked", says: "line 7, in summary: summary called average. The traceback lists every call that was still waiting for an answer." },
        { label: "4. the top: your program's line", says: 'line 11, in <module>: the main program called summary("Tuesday", []). An empty list: there is the real cause.' },
        { label: "5. fix the cause, not the symptom", says: "The crash is in average, but the question is: what should the average of no amounts be? Decide that, and the error is gone for good." },
      ]}
    />
  );
}

/** Python from zero, chapter 11: how Python works through a list comprehension, played step by step. */
function ComprehensionSteps() {
  return (
    <SketchSteps
      title="[a * 2 for a in [120, 45, 900] if a > 100]"
      intro="Press Play to watch Python build the new list, one item at a time."
      label="Python starts an empty result list, takes each item in turn, tests the if condition, works out the expression at the front for the items that pass, appends each answer, and gives back the new list 240 and 1800"
      steps={[
        { label: "1. an empty new list", says: "Behind the scenes Python starts a new, empty list. The original list is never touched." },
        { label: "2. a = 120: is 120 > 100?", says: "It takes the first item and tests the if part. 120 is over 100: yes." },
        { label: "3. work out a * 2: 240", says: "The expression at the front runs for the item that passed, and 240 is added to the new list." },
        { label: "4. a = 45: is 45 > 100?", says: "No. The item is skipped: the expression does not even run for it." },
        { label: "5. a = 900: yes, add 1800", says: "900 passes the test, so 900 * 2 = 1800 joins the new list." },
        { label: "6. the answer: [240, 1800]", says: "No items left. The whole comprehension becomes the new list, [240, 1800]." },
      ]}
    />
  );
}

/** Python from zero, chapter 13: what Python does when an error happens inside try, played step by step. */
function TryExceptFlow() {
  return (
    <SketchSteps
      title='try: amount = float("abc")'
      intro="Press Play to follow one error from the line that raises it to the except that handles it."
      label="Python runs the lines inside try one by one; float of abc raises a ValueError; the rest of the try block is skipped; Python looks for an except that matches ValueError and runs it; then the program carries on after the whole try statement"
      steps={[
        { label: "1. enter try: watch for errors", says: "Python starts running the indented lines under try, one at a time, ready to react if one of them raises an exception." },
        { label: '2. float("abc") raises ValueError', says: "The text is not a number, so float raises a ValueError. Normally that would stop the whole program." },
        { label: "3. skip the rest of try", says: "Nothing after the failing line inside try runs. print(\"ok:\", amount) is skipped: there is no amount to print." },
        { label: "4. find a matching except", says: "Python looks at the except blocks in order. except ValueError matches the kind of error that was raised." },
        { label: "5. run the except block", says: "The except block runs instead: print(\"skipped:\", text). The error has been handled." },
        { label: "6. carry on after try", says: "The program continues with the next line after the whole try statement, as if nothing had crashed. In a loop, that means the next value." },
      ]}
    />
  );
}

/** Python from zero, chapter 15: what happens in pen = Item("pen", 15), played step by step. */
function ObjectCreation() {
  return (
    <SketchSteps
      title='pen = Item("pen", 15)'
      intro="Press Play to watch Python build one object from the class."
      label="Python makes a new empty Item object, calls __init__ with self set to that object and the arguments pen and 15, __init__ stores name and price on the object, and the finished object is stored in the variable pen"
      steps={[
        { label: "1. a new, empty Item", says: "Python makes a brand-new object of the class Item. It has no name and no price yet: nothing has been stored on it." },
        { label: '2. call __init__(self, "pen", 15)', says: "Python calls __init__ automatically. self is the new object; name is \"pen\" and price is 15." },
        { label: '3. self.name = "pen"', says: "This stores the name on this object. It is the object's own attribute, separate from every other Item." },
        { label: "4. self.price = 15", says: "Now the object has both attributes. __init__ is done; it returns nothing, it only set the object up." },
        { label: "5. pen is the finished object", says: "The new object is the result of Item(\"pen\", 15), and it is stored in pen. pen.name is \"pen\", pen.price is 15." },
      ]}
    />
  );
}

/** Python from zero, chapter 16: where Python looks when it meets import money, played step by step. */
function ImportSearch() {
  return (
    <SketchSteps
      title="import money"
      intro="Press Play to follow Python's search for a module."
      label="Python first checks whether money was already imported in this program; then looks in the folder of the script it is running; then in the standard library that comes with Python; then in the installed packages, such as a virtual environment's; if it is nowhere, it raises ModuleNotFoundError"
      steps={[
        { label: "1. already imported?", says: "If this program imported money before, Python reuses it at once. A module's file runs only the first time it is imported." },
        { label: "2. the script's own folder", says: "Next, the folder of the program you ran. money.py next to tracker.py is found right here." },
        { label: "3. the standard library", says: "Then the modules that ship with Python: csv, json, statistics, math and hundreds more." },
        { label: "4. installed packages", says: "Then the packages installed with pip: in a virtual environment, only that environment's own packages." },
        { label: "5. nowhere: ModuleNotFoundError", says: "If no step found it, Python stops with ModuleNotFoundError: No module named 'money'. Check the file name and the folder." },
      ]}
    />
  );
}

/** Java from zero, chapter 1: what happens after "java First.java", played step by step. */
function JavaRunsAFile() {
  return (
    <SketchSteps
      title="java First.java"
      intro="Press Play to watch Java turn your file into a running program."
      label="You type java First.java; Java reads the whole file and checks its grammar and types; it compiles the class to bytecode; the Java Virtual Machine loads the class, finds main and runs its lines one at a time; println sends text to the terminal; when main ends, the program ends"
      steps={[
        { label: "1. you press Enter", says: "The terminal starts java and hands it your file, First.java." },
        { label: "2. check the whole file", says: "Java reads every line first: grammar, names and types. One missing ; or a misspelled name and nothing runs: you get a compile error." },
        { label: "3. compile to bytecode", says: "Your class becomes bytecode: simple instructions that are the same on every computer. (javac First.java writes them to First.class.)" },
        { label: "4. the JVM loads the class", says: "The Java Virtual Machine, a program made for this exact computer, loads the bytecode. This is the trick behind \"write once, run anywhere\"." },
        { label: "5. find main, run it line by line", says: "The JVM looks for public static void main and runs its lines from the top, one at a time." },
        { label: "6. main ends: the program ends", says: "Each println sends a line to the terminal. When main reaches its closing brace, the program is over." },
      ]}
    />
  );
}

/** Java from zero, chapter 2: one method call, from the call to the value coming back. */
function JavaMethodCall() {
  return (
    <SketchSteps
      title='String message = welcome("Pune");'
      intro="Press Play to follow one method call, from the call to the answer."
      label="main calls welcome with the argument Pune; Java jumps into the method; the parameter city holds Pune; the body joins the strings; return carries Welcome to Pune! back; main stores it in message, a String variable"
      steps={[
        { label: '1. the call: welcome("Pune")', says: "main reaches the right side of = and sees a method name with brackets: call it." },
        { label: "2. jump into the method", says: "Java remembers where it was in main, then jumps to static String welcome(String city)." },
        { label: '3. city = "Pune"', says: "The parameter city holds the argument for this call. Java already checked at compile time that \"Pune\" is a String." },
        { label: "4. the body runs", says: 'The body joins "Welcome to ", city and "!" into one String: "Welcome to Pune!".' },
        { label: "5. return hands it back", says: "return ends the method and carries the String back to main. The method's own city variable is gone." },
        { label: "6. message holds the answer", says: "Back in main, the String is stored in message, and the next line prints it." },
      ]}
    />
  );
}

/** Java from zero, chapter 6: reading a Java stack trace, which lists the newest call first. */
function JavaStackTrace() {
  return (
    <SketchSteps
      title="reading a Java stack trace"
      intro="Press Play to read a real stack trace the way Java developers do: from the top."
      label="Read the first line: the exception and its message. Then the first at line: the method, file and line where it happened. Then the lines below: the methods that called it, oldest at the bottom, ending in main"
      steps={[
        { label: "1. the first line: what went wrong", says: "Exception in thread \"main\" java.lang.ArithmeticException: / by zero. The kind of exception, then its message." },
        { label: "2. the first at line: where", says: "at Report.average(Report.java:8): the method, the file and the line number. This is where the exception was thrown." },
        { label: "3. the next line: who called it", says: "at Report.summary(Report.java:12): summary called average. Java lists the calls newest first, the opposite of Python." },
        { label: "4. the last line: the start", says: "at Report.main(Report.java:17): main called summary with an empty array of fines. There is the real cause." },
        { label: "5. fix the cause", says: "The crash is in average, but the question is what the average of no fines should be. Decide that, and the error is gone for good." },
      ]}
    />
  );
}

/** Java from zero, chapter 9: what new Book("The Hobbit", 2) does, played step by step. */
function JavaObjectCreation() {
  return (
    <SketchSteps
      title='Book hobbit = new Book("The Hobbit", 2);'
      intro="Press Play to watch Java build one object."
      label="new makes an empty Book object with default field values; the constructor runs with this pointing at the new object; it stores the title and the copies; new gives back a reference, which is stored in hobbit"
      steps={[
        { label: "1. new: an empty Book", says: "Java finds room in memory for one Book and fills its fields with defaults: title is null, copies is 0." },
        { label: '2. the constructor runs', says: 'Java calls Book("The Hobbit", 2). Inside it, this means the brand-new object; title and copies are the parameters.' },
        { label: '3. this.title = title', says: 'The object\'s own title field now holds "The Hobbit". Because it is final, it can never change again.' },
        { label: "4. this.copies = copies", says: "The object's copies field holds 2. The constructor ends: the object is ready." },
        { label: "5. hobbit holds a reference", says: "new gives back a reference to the object, and it is stored in hobbit. hobbit.borrow() now works on this book and no other." },
      ]}
    />
  );
}

/** Java from zero, chapter 13: what happens when a line inside try throws, played step by step. */
function JavaTryCatch() {
  return (
    <SketchSteps
      title='Integer.parseInt("twelve")'
      intro="Press Play to follow an exception from the line that throws to the catch that handles it."
      label="Java runs the try block line by line; parseInt cannot read twelve and throws a NumberFormatException; the rest of the try block is skipped; Java finds the catch whose type matches and runs it; the program carries on after the catch; if no catch matches, the exception travels up to the caller, and if nobody catches it the program stops with a stack trace"
      steps={[
        { label: "1. run the try block", says: "Java runs the lines inside try { } from the top, as usual." },
        { label: '2. parseInt("twelve") throws', says: "parseInt cannot read twelve as a number. It creates a NumberFormatException object and throws it." },
        { label: "3. skip the rest of try", says: "The println after parseInt never runs. Java leaves the try block at once." },
        { label: "4. find a matching catch", says: "catch (NumberFormatException e) matches, so e is the exception object and the catch block runs." },
        { label: "5. carry on", says: "After the catch, the loop continues with the next value. One bad value did not stop the others." },
        { label: "6. no catch? up to the caller", says: "With no matching catch, the exception leaves the method and goes to its caller, then its caller. If nobody catches it, the program stops with a stack trace." },
      ]}
    />
  );
}

/** JavaScript from zero, chapter 1: what happens after "node first.js", played step by step. */
function NodeRunsAFile() {
  return (
    <SketchSteps
      title="node first.js"
      intro="Press Play to watch Node turn your file into a running program."
      label="You type node first.js; Node reads the whole file; it checks the grammar, and a SyntaxError stops everything before any line runs; then it runs the lines from top to bottom; a line that goes wrong while running stops the program at that line, after the lines before it already ran; when the last line is done, the program ends"
      steps={[
        { label: "1. you press Enter", says: "The terminal starts node and hands it your file, first.js." },
        { label: "2. read the whole file", says: "Node reads every line before running any of them." },
        { label: "3. check the grammar", says: "Every bracket closed, every quote ended? One grammar mistake is a SyntaxError, and not a single line runs." },
        { label: "4. run from the top", says: "The V8 engine runs the lines one at a time, top to bottom. Each console.log prints a line." },
        { label: "5. a line goes wrong?", says: "A ReferenceError or a TypeError stops the program at that line. The lines before it already ran and already printed." },
        { label: "6. the last line: done", says: "When the last line has run, the program is over and the terminal is yours again." },
      ]}
    />
  );
}

/** JavaScript from zero, chapter 6: reading a Node stack trace, played step by step. */
function JsStackTrace() {
  return (
    <SketchSteps
      title="TypeError: Cannot read properties of undefined"
      intro="Press Play to read a stack trace the way JavaScript developers do."
      label="The first lines show the file, the line and a caret under the exact spot; the error line says what kind of problem it is; the first at line names the function and line where it happened; the next at line shows who called it; lines from node internal are Node's own machinery and can be skipped"
      steps={[
        { label: "1. report.js:13 and a ^", says: "The file, the line, and a little arrow under the exact spot that failed." },
        { label: "2. TypeError: ...", says: "What went wrong, in one sentence: something was undefined, and code asked it for toUpperCase." },
        { label: "3. at headline (report.js:13)", says: "The newest call comes first: it failed inside headline, on line 13." },
        { label: "4. at Object.<anonymous> (report.js:17)", says: "Who called headline: the top of the file itself, line 17. Read upward to follow the story forward." },
        { label: "5. at Module._compile ... node:internal", says: "Node's own machinery that started your file. Skip it: the first lines that name your file are the ones that matter." },
      ]}
    />
  );
}

/** JavaScript from zero, chapter 15: the event loop, played step by step on the four-line puzzle. */
function JsEventLoop() {
  return (
    <SketchSteps
      title="1. start, 2. timer, 3. promise, 4. end"
      intro="Press Play to follow JavaScript's one worker through the four lines."
      label="The call stack runs line 1 and prints start; setTimeout hands its job to the timer queue; then the promise hands its job to the promise queue; line 4 prints end and the call stack is empty; now every promise job runs, printing promise; only then does the next timer job run, printing timer; and the loop waits for more work"
      steps={[
        { label: "1. run line 1", says: "One worker, the call stack, runs your code from the top: it prints 1. start." },
        { label: "2. setTimeout: to the timer queue", says: "The timer's job is not run now. It waits in the timer queue, even with 0 ms." },
        { label: "3. then: to the promise queue", says: "The promise's job waits too, in a separate, faster queue: the promise queue." },
        { label: "4. run line 4", says: "The worker carries on with your code and prints 4. end. Now your code is finished." },
        { label: "5. empty stack: promise jobs first", says: "With nothing else to do, the event loop runs every waiting promise job: 3. promise." },
        { label: "6. then one timer job", says: "Only then does it take the next timer job: 2. timer, after 0 ms. And it goes round again, waiting for more work." },
      ]}
    />
  );
}

/** Go from zero, chapter 1: what happens after "go run first.go", played step by step. */
function GoRunsAFile() {
  return (
    <SketchSteps
      title="go run first.go"
      intro="Press Play to watch Go turn your file into a running program."
      label="You type go run first.go; Go reads the whole file and checks grammar, names, types and unused variables or imports; any problem is a compile error and nothing runs; then it compiles the file to machine code; the program starts at func main and runs line by line; a panic stops it at that line; when main returns, the program ends"
      steps={[
        { label: "1. you press Enter", says: "The terminal starts go and hands it your file, first.go." },
        { label: "2. check everything", says: "Grammar, names and types, and anything declared but never used. One problem is a compile error, and nothing runs." },
        { label: "3. compile to machine code", says: "Go turns the file into a real program for this computer, in about a second." },
        { label: "4. start at func main", says: "The program runs the lines of main from the top, one at a time." },
        { label: "5. a panic?", says: "Something impossible while running, like parcel number 5 of 2, panics: the program stops at that line." },
        { label: "6. main returns: the end", says: "When main reaches its closing brace, the program is over." },
      ]}
    />
  );
}

/** Go from zero, chapter 6: reading a Go panic, played step by step. */
function GoPanicTrace() {
  return (
    <SketchSteps
      title="panic: index out of range [0] with length 0"
      intro="Press Play to read a Go panic the way Go developers do."
      label="The first line says what went wrong; goroutine 1 running means the main goroutine; the first function listed is where it happened, with the file and line on the next line; each function below called the one above it; main.main is where the program started"
      steps={[
        { label: "1. panic: ...", says: "What went wrong: asked for item 0 of a list with 0 items." },
        { label: "2. goroutine 1 [running]", says: "Which goroutine crashed. Number 1 is the main one (chapter 16 makes more)." },
        { label: "3. main.heaviest ... report.go:9", says: "The newest call comes first: it failed in heaviest, at line 9." },
        { label: "4. main.summary ... report.go:19", says: "Who called heaviest: summary, at line 19. The strange hex numbers are the arguments' raw memory: skip them." },
        { label: "5. main.main ... report.go:24", says: "Where it all began: main, line 24. Read upward to follow the story forward." },
      ]}
    />
  );
}

/** Go from zero, chapter 16: three goroutines report back through one channel, played step by step. */
function GoChannels() {
  return (
    <SketchSteps
      title="results := make(chan string)"
      intro="Press Play to watch goroutines hand their results back through a channel."
      label="main makes a channel; it starts three goroutines with go, which run alongside main; main reaches a receive and waits; the goroutine that finishes first sends its result into the channel and main receives it; the other two follow in the order they finish; after three receives, main carries on"
      steps={[
        { label: "1. make the channel", says: "main makes a channel of strings: a pipe that goroutines can send into." },
        { label: "2. go, go, go", says: "Three goroutines start, each weighing one parcel. They run alongside main, not one after another." },
        { label: "3. main waits at <-results", says: "Receiving blocks: main waits until something is sent. No busy checking, no shared variables." },
        { label: "4. the first to finish sends", says: "Whichever goroutine finishes first sends its result, and main receives it at once. Here that is P-3." },
        { label: "5. the others follow", says: "The next two results arrive in the order their goroutines finish, not the order they started." },
        { label: "6. three received: carry on", says: "After three receives, main has every result and carries on." },
      ]}
    />
  );
}

/* ---------- Redis in practice: playing timelines ---------- */

function LatencyLadder() {
  return (
    <SketchSteps
      title="where the time goes"
      intro="Press Play to climb down the ladder. Each rung is a place data can live, and each is far slower than the one above."
      label="the CPU cache answers in half a nanosecond; main memory in about 100 nanoseconds; an SSD read in about 150 microseconds; a round trip inside a data centre in about half a millisecond; a hard disk seek in about 10 milliseconds; a packet across the world in about 150 milliseconds"
      steps={[
        { label: "CPU cache: 0.5 ns", says: "Data the processor just used. If memory took one second, this would take a blink." },
        { label: "RAM: 100 ns", says: "Main memory, where Redis keeps everything. Our one-second yardstick." },
        { label: "SSD read: 150 µs", says: "About 1,500 times slower than RAM. On our scale: 25 minutes." },
        { label: "Data centre round trip: 0.5 ms", says: "Asking another server in the same building. On our scale: 1 hour 23 minutes." },
        { label: "Hard disk seek: 10 ms", says: "A spinning disk moving its head to the right place. On our scale: more than a day." },
        { label: "Across the world: 150 ms", says: "California to the Netherlands and back. On our scale: 17 days." },
      ]}
    />
  );
}

function HitRateSavings() {
  return (
    <SketchSteps
      title="100 price reads, a 90% hit rate"
      intro="Press Play to follow 100 reads of prices through the cache."
      label="100 reads arrive; Redis answers 90 of them from memory in under a millisecond each; only 10 misses go to the slow catalogue; each miss costs 1.5 seconds and 10 paise; the answer is stored, so the next read is a hit; total: 10 calls instead of 100"
      steps={[
        { label: "1. 100 reads arrive", says: "Customers open product pages. Every page needs a price." },
        { label: "2. 90 hits: Redis answers", says: "The price is already in Redis. Each answer takes a fraction of a millisecond and costs nothing extra." },
        { label: "3. 10 misses: ask the catalogue", says: "These prices were not cached yet, or had expired. Each one waits 1.5 seconds and costs Rs 0.10." },
        { label: "4. Store each answer", says: "The app keeps every catalogue answer in Redis, so the next read of that price is a hit." },
        { label: "5. 10 calls, not 100", says: "The catalogue did a tenth of the work. Raise the hit rate to 99% and it does a hundredth." },
      ]}
    />
  );
}

function OneAtATime() {
  return (
    <SketchSteps
      title="three clients, one Redis"
      intro="Press Play to watch Redis serve three clients that send commands at the same moment."
      label="the Kothrud app, the Baner app and a worker each send a command at once; Redis puts them in a line; it runs the first command from start to finish; then the second; then the third; no command ever runs in the middle of another"
      steps={[
        { label: "1. Three commands arrive at once", says: "The Kothrud app sends INCR orders:today, the Baner app sends INCR orders:today, a worker sends GET stock:eggs." },
        { label: "2. They wait in line", says: "Redis has one main thread. It takes commands one at a time, in the order they arrived." },
        { label: "3. INCR from Kothrud: 1", says: "Read, add one, write: all inside one command. Nothing else runs meanwhile." },
        { label: "4. INCR from Baner: 2", says: "This one sees the 1 that Kothrud just wrote, so no count is lost." },
        { label: "5. GET from the worker", says: "It reads the stock. Each command took microseconds, so nobody waited long." },
        { label: "6. The catch", says: "If one command took a whole second, the other two would wait a whole second. Chapter 17 is about that." },
      ]}
    />
  );
}

function CacheAsideFlow() {
  return (
    <SketchSteps
      title="GET /price/rice, cache-aside"
      intro="Press Play to follow two requests for the same price: the first misses, the second hits."
      label="a request asks for the price of rice; the app asks Redis for price:rice; it is missing; the app asks the catalogue and waits 1.5 seconds; it stores the answer in Redis for 60 seconds; it answers; a second request asks Redis and finds it; it answers in about a millisecond"
      steps={[
        { label: "1. GET /price/rice arrives", says: "A customer opens the rice page. The app needs the price." },
        { label: "2. Ask Redis: GET price:rice", says: "Always look in the cache first. It answers (nil): a miss." },
        { label: "3. Miss: ask the catalogue", says: "The slow, paid call: 1.5 seconds and Rs 0.10. It answers 60." },
        { label: "4. Keep it: SET price:rice 60 EX 60", says: "Store the answer with a lifetime, so a price change shows up within a minute at most." },
        { label: "5. Answer the customer", says: "This first customer waited 1.5 seconds." },
        { label: "6. Next request: a hit", says: "GET price:rice finds 60 at once. This customer waits about a millisecond, and the catalogue is not asked." },
      ]}
    />
  );
}

function Stampede() {
  return (
    <SketchSteps
      title="a sale starts: 30 requests, one empty cache"
      intro="Press Play to see a stampede, then the lock that stops it."
      label="the cached price of paneer expires; 30 requests arrive in the same instant; without a lock all 30 miss and all 30 ask the catalogue; with a lock one request wins it and asks; the other 29 wait briefly and read the answer from Redis; one catalogue call instead of 30"
      steps={[
        { label: "1. price:paneer expires", says: "Its 60 seconds are up, just as a sale on paneer starts." },
        { label: "2. 30 requests, same instant", says: "Every one of them asks Redis, and every one gets a miss." },
        { label: "3. No lock: 30 catalogue calls", says: "All 30 ask the slow catalogue at once: 30 times the cost, and it may fall over." },
        { label: "4. With a lock: one winner", says: "SET lock:price:paneer 1 NX EX 5 succeeds for exactly one request. Only it asks the catalogue." },
        { label: "5. The other 29 wait a moment", says: "They sleep 100 ms and look in Redis again, until the winner has stored the price." },
        { label: "6. One call, 30 answers", says: "The catalogue answered once. Everyone got the price about 1.5 seconds after asking." },
      ]}
    />
  );
}

function LockFlow() {
  return (
    <SketchSteps
      title="two customers, one delivery slot"
      intro="Press Play to watch a Redis lock decide who books the slot."
      label="Asha and Ravi book the 6 pm slot at the same moment; both try SET lock NX with a token and an expiry; Asha's succeeds and Ravi's returns nil; Ravi gets a 409; Asha checks the slot is free, books it, and releases the lock only if it still holds her token"
      steps={[
        { label: "1. Two bookings, same instant", says: "Asha and Ravi both tap the 6 pm delivery slot." },
        { label: "2. Both: SET lock NX PX 2000", says: "Each request tries to create the lock key with its own random token and a 2 second expiry." },
        { label: "3. Asha wins: OK", says: "NX writes only when the key is missing, so exactly one SET succeeds." },
        { label: "4. Ravi loses: (nil), 409", says: "His SET found the key there. He is told politely that someone is booking." },
        { label: "5. Asha books the slot", says: "Only the lock holder checks and writes booking:slot:1800. No race is possible." },
        { label: "6. Release, if still hers", says: "A small script deletes the lock only if it still holds Asha's token, never someone else's." },
      ]}
    />
  );
}

function SlowCommand() {
  return (
    <SketchSteps
      title="one slow command, everyone waits"
      intro="Press Play to see why one big command hurts every other client."
      label="a report sends ZRANGE over 100,000 members; Redis starts it on its one thread; meanwhile thousands of quick GETs from the apps arrive and wait in line; the ZRANGE finishes after many milliseconds; only then are the waiting GETs served; the slow log records the ZRANGE"
      steps={[
        { label: "1. A report sends one big ZRANGE", says: "It asks for all 100,000 members of report:2025 at once." },
        { label: "2. Redis starts it", says: "One thread, one command at a time: this command now has Redis to itself." },
        { label: "3. Quick GETs pile up", says: "The store apps keep asking for prices and sessions. Each would take microseconds, but they must wait." },
        { label: "4. The ZRANGE finishes", says: "Many milliseconds later it sends its huge answer. Every waiting client was slow for that long." },
        { label: "5. The queue drains", says: "The waiting GETs are served, a little late each. Customers saw a slow app." },
        { label: "6. The slow log remembers", says: "Redis noted the command, its key and its duration, so you can find it later with SLOWLOG GET." },
      ]}
    />
  );
}

function EvictionLru() {
  return (
    <SketchSteps
      title="Redis is full: volatile-lru"
      intro="Press Play to see what Redis does when a write arrives and memory is full."
      label="memory reaches maxmemory; a new write arrives; with noeviction Redis refuses it with an OOM error; with volatile-lru Redis looks only at keys that have a TTL; it removes the one used least recently; carts and sessions without a TTL are never touched; the write succeeds"
      steps={[
        { label: "1. Memory reaches maxmemory", says: "Redis has used its whole budget: 64 MB in this lab." },
        { label: "2. A new write arrives", says: "A customer adds rice to their cart." },
        { label: "3. noeviction: refuse it", says: "The write fails with OOM. Carts, logins and counters stop working." },
        { label: "4. volatile-lru: pick a victim", says: "Redis looks only at keys with a TTL (cache entries) and picks one not used for the longest time." },
        { label: "5. Evict it", says: "That old cached page is removed. It can be fetched again later; nothing real is lost." },
        { label: "6. The write succeeds", says: "The cart is saved. Keys without a TTL were never candidates." },
      ]}
    />
  );
}

/* ---------- SQL from zero ---------- */

function LeftJoin() {
  return (
    <SketchSteps
      title="passengers LEFT JOIN bookings"
      intro="Press Play to watch a join pair rows, and see what a LEFT JOIN keeps that an inner join drops."
      label="Asha has two bookings, Ravi has none, Meera has one; the join pairs each passenger with every matching booking; Asha appears twice and Meera once; an inner join drops Ravi; a left join keeps Ravi once with NULL in the booking columns; WHERE booking id IS NULL then keeps only Ravi"
      steps={[
        { label: "1. Take each passenger", says: "Asha, Ravi and Meera, from the table before JOIN (the left table)." },
        { label: "2. Find matching bookings", says: "ON b.passenger_id = p.id: Asha matches two bookings, Meera one, Ravi none." },
        { label: "3. One row per pair", says: "Asha appears twice, once with each booking. Joins multiply rows." },
        { label: "4. Inner JOIN: Ravi is gone", says: "A passenger with no match makes no pair, so an inner join drops him." },
        { label: "5. LEFT JOIN: Ravi stays", says: "Every left row stays at least once. Ravi's booking columns are NULL." },
        { label: "6. WHERE b.id IS NULL", says: "Keeps only the rows with no match: the passengers who never booked." },
      ]}
    />
  );
}

/* ---------- Git without fear ---------- */

function GitThreeAreas() {
  return (
    <SketchSteps
      title="working folder, staging area, history"
      intro="Press Play to follow one change from your editor into history."
      label="you edit trails.md in the working folder; git status shows it modified; git add copies it into the staging area; git status shows it staged; git commit saves everything staged as a new commit in history; the staging area now matches the commit"
      steps={[
        { label: "1. Edit a file", says: "You change trails.md. The change exists only in your working folder." },
        { label: "2. git status: modified", says: "Git notices the file differs from the last commit, but nothing is staged yet." },
        { label: "3. git add trails.md", says: "The change is copied into the staging area: it will be in the next commit." },
        { label: "4. git status: staged", says: "Changes to be committed: trails.md. Other edits can stay unstaged." },
        { label: "5. git commit -m ...", says: "Everything staged becomes one new commit in history, with your message." },
        { label: "6. Clean again", says: "Working folder, staging area and the last commit all match. git status: nothing to commit." },
      ]}
    />
  );
}

function GitBranchPointer() {
  return (
    <SketchSteps
      title="a branch is a label on a commit"
      intro="Press Play to watch branch labels move as you commit."
      label="main points at commit B; git switch -c feature makes a second label on B and HEAD follows it; a commit C on feature moves only the feature label; main still points at B; git switch main moves HEAD back to main"
      steps={[
        { label: "1. main points at B", says: "A branch is just a label holding one commit's hash. HEAD says you are on main." },
        { label: "2. git switch -c feature", says: "A new label, feature, on the same commit B. No files are copied. HEAD now follows feature." },
        { label: "3. Commit C on feature", says: "The new commit's parent is B. The label you are on, feature, moves to C." },
        { label: "4. main has not moved", says: "main still points at B. Nobody on main sees C yet." },
        { label: "5. git switch main", says: "HEAD moves back to main, and your files become B's files again." },
      ]}
    />
  );
}

function GitMerge() {
  return (
    <SketchSteps
      title="fast-forward or merge commit"
      intro="Press Play to see the two kinds of merge."
      label="if main has not moved since the branch started, git merge just slides the main label forward, a fast-forward; if both main and the branch have new commits, git merge makes a merge commit with two parents that joins both lines"
      steps={[
        { label: "1. Branch ahead, main still", says: "feature has new commits; main has not moved since the branch began." },
        { label: "2. Fast-forward", says: "git merge feature slides the main label forward. No new commit is needed." },
        { label: "3. Both sides moved", says: "Now main and the branch each have commits the other lacks: history has forked." },
        { label: "4. Merge commit", says: "git merge makes a commit with two parents, joining both lines." },
        { label: "5. Delete the branch label", says: "git branch -d removes the label; its commits stay in history." },
      ]}
    />
  );
}

function GitConflict() {
  return (
    <SketchSteps
      title="a merge conflict, start to finish"
      intro="Press Play to walk through a conflict calmly."
      label="both branches changed the same line; git merge stops and writes both versions between markers; you edit the file to say what is true and delete the markers; git add marks it resolved; git commit finishes the merge"
      steps={[
        { label: "1. Same line, two changes", says: "main says 15.5 km; ravi/rajmachi says 16 km. Git cannot choose." },
        { label: "2. Merge pauses", says: "CONFLICT in trails.md. Everything else is merged; this file waits for you." },
        { label: "3. Read the markers", says: "Your side between <<<<<<< and =======, theirs between ======= and >>>>>>>." },
        { label: "4. Edit to the truth", says: "Keep one side, both, or write something new. Delete the three marker lines." },
        { label: "5. git add trails.md", says: "Staging the file tells Git it is resolved." },
        { label: "6. git commit", says: "The merge commit is made. Or, at any point before: git merge --abort." },
      ]}
    />
  );
}

function GitUndoMap() {
  return (
    <SketchSteps
      title="which undo for which place"
      intro="Press Play to match each mistake with its undo."
      label="an edit only in the working folder is thrown away with git restore; a staged change is unstaged with git restore --staged; the last unpushed commit is replaced with git commit --amend; recent unpushed commits are undone with git reset --soft; pushed commits are undone with git revert"
      steps={[
        { label: "Edit not staged", says: "git restore file: back to the last commit. The edit is gone for good." },
        { label: "Staged by mistake", says: "git restore --staged file: unstaged, and the edit stays in the file." },
        { label: "Last commit, not pushed", says: "git commit --amend: a new commit replaces it." },
        { label: "Recent commits, not pushed", says: "git reset --soft HEAD~1: the branch steps back, the changes stay staged." },
        { label: "Already pushed", says: "git revert: a new commit that undoes it, safe for everyone (chapter 7)." },
      ]}
    />
  );
}

function GitReflog() {
  return (
    <SketchSteps
      title="the reflog after a hard reset"
      intro="Press Play to recover a commit that seemed lost."
      label="a commit D is made; git reset --hard HEAD~1 moves main back to C; git log no longer shows D; git reflog lists where HEAD has been, including D; git branch rescued D gives the commit a label again"
      steps={[
        { label: "1. Commit D", says: "Asha commits Add Visapur on top of C." },
        { label: "2. git reset --hard HEAD~1", says: "main moves back to C. D is no longer on any branch." },
        { label: "3. git log: D is gone", says: "History starts at C. It looks deleted, but the commit still exists." },
        { label: "4. git reflog", says: "Every move of HEAD is listed: HEAD@{1} is D, just before the reset." },
        { label: "5. git branch rescued HEAD@{1}", says: "A label on D again. The commit is safe." },
      ]}
    />
  );
}

function GitStash() {
  return (
    <SketchSteps
      title="stash, switch, fix, pop"
      intro="Press Play to follow an urgent fix in the middle of your work."
      label="you have unfinished changes on feature; git stash puts them in the stash and cleans the folder; you switch to main and commit the fix; you switch back to feature; git stash pop brings the changes back"
      steps={[
        { label: "1. Unfinished work", says: "Half-written Lohagad lines on feature/lohagad, not committed." },
        { label: "2. git stash", says: "The changes go into the stash; the folder matches the last commit again." },
        { label: "3. Switch to main, fix, commit", says: "The spelling fix goes into main, alone." },
        { label: "4. Back to the branch", says: "git switch feature/lohagad." },
        { label: "5. git stash pop", says: "Your unfinished lines are back, and the stash is empty again." },
      ]}
    />
  );
}

function GitPushPull() {
  return (
    <SketchSteps
      title="fetch, pull and push"
      intro="Press Play to see commits move between your copy and the server."
      label="Ravi pushes a commit to the server; git fetch downloads it and moves origin/main, while your main stays; git pull also merges it into main; you commit; git push uploads your commit and moves the server's main"
      steps={[
        { label: "1. Ravi pushes", says: "The server's main gains a commit you do not have." },
        { label: "2. git fetch", says: "Your copy downloads it. origin/main moves; your main does not." },
        { label: "3. git pull", says: "Fetch plus merge: your main now has Ravi's commit too." },
        { label: "4. You commit", says: "Your main is one commit ahead of origin/main." },
        { label: "5. git push", says: "Your commit goes up, and the server's main moves to it." },
      ]}
    />
  );
}

function GitPullRequest() {
  return (
    <SketchSteps
      title="a pull request"
      intro="Press Play to follow one change through review."
      label="make a branch and commit; push the branch to the server; a teammate reviews the diff since main; you commit the requested fix on the same branch and push; the branch is merged into main and pushed"
      steps={[
        { label: "1. Branch and commit", says: "feature/torna, from an up-to-date main." },
        { label: "2. git push -u origin feature/torna", says: "The branch is on the server; the pull request shows its diff." },
        { label: "3. Review", says: "A teammate reads git diff main...feature/torna and asks for a change." },
        { label: "4. Fix and push again", says: "A new commit on the same branch; the pull request updates itself." },
        { label: "5. Merge into main", says: "The approved branch is merged and main is pushed. The branch can be deleted." },
      ]}
    />
  );
}

function GitRebase() {
  return (
    <SketchSteps
      title="rebase onto main"
      intro="Press Play to watch commits being replayed."
      label="the branch started from an old commit; main moved on; git rebase main sets the branch's commits aside, moves the branch to the tip of main, and replays each commit as a new commit; history becomes one straight line"
      steps={[
        { label: "1. History has forked", says: "Your three commits started from A; main has two newer commits." },
        { label: "2. Set your commits aside", says: "Rebase remembers the changes your commits made." },
        { label: "3. Move to main's tip", says: "The branch now starts from the latest main." },
        { label: "4. Replay, one by one", says: "Each change is applied again as a new commit, with a new hash." },
        { label: "5. One straight line", says: "Merged into main now, it is a fast-forward. Never rebase commits others have." },
      ]}
    />
  );
}

function GitObjects() {
  return (
    <SketchSteps
      title="commit, tree, blob"
      intro="Press Play to walk from a commit down to a file's content."
      label="a commit names a tree and its parent; the tree lists names, each pointing at a blob or another tree; a blob holds a file's content; every object's name is the hash of its content, so a change anywhere changes the hashes above it"
      steps={[
        { label: "1. The commit", says: "git cat-file -p HEAD: a tree hash, the parent, author, date and message." },
        { label: "2. The tree", says: "A list of names: tips.md is a blob, maps is another tree." },
        { label: "3. The blob", says: "Just the content of tips.md. Its name is the hash of that content." },
        { label: "4. Same content, same blob", says: "An unchanged file in the next commit reuses its blob: no copy." },
        { label: "5. A chain of hashes", says: "Each commit holds its parent's hash, so changing the past changes every hash after it." },
      ]}
    />
  );
}

function LinuxTree() {
  return (
    <SketchSteps
      title="one tree of folders"
      intro="Press Play to walk from the root down to tonight's plan."
      label="everything starts at the root, slash; the system's folders hang from it; workspace holds this course; a path names each folder on the way down; dot dot goes one level up"
      steps={[
        { label: "1. The root, /", says: "One tree for the whole machine: no drive letters." },
        { label: "2. System folders", says: "/etc for settings, /var/log for logs, /home for people, /tmp for scratch." },
        { label: "3. /workspace/01-why-linux", says: "Your work for this course, one folder per chapter." },
        { label: "4. tara/observations/2026/november/23", says: "Each slash is one more folder down: that is a path." },
        { label: "5. cd ..", says: "Two dots climb one level back up. A path starting with / always starts from the root." },
      ]}
    />
  );
}

function LinuxGlob() {
  return (
    <SketchSteps
      title="the shell expands the pattern"
      intro="Press Play to see what rm really receives."
      label="you type rm downloads star dot tmp; the shell looks in the folder for names that match; it replaces the pattern with the three matching names; rm runs with three names and never sees the star"
      steps={[
        { label: "1. You type", says: "rm downloads/*.tmp" },
        { label: "2. The shell looks", says: "Which names in downloads end in .tmp? cache-1.tmp, cache-2.tmp, upload.tmp." },
        { label: "3. The pattern is replaced", says: "rm downloads/cache-1.tmp downloads/cache-2.tmp downloads/upload.tmp" },
        { label: "4. rm runs", says: "rm gets three names. It never sees the star. echo shows the same list first, safely." },
      ]}
    />
  );
}

function LinuxStreams() {
  return (
    <SketchSteps
      title="three streams"
      intro="Press Play to send each stream somewhere new."
      label="a program reads from stream 0 and writes results to stream 1 and problems to stream 2; normally both go to the screen; greater than sends stream 1 to a file; two greater than sends stream 2 to another file; two greater than ampersand one joins them"
      steps={[
        { label: "1. One program, three streams", says: "0 in (keyboard), 1 out (results), 2 out (problems)." },
        { label: "2. Normally", says: "Streams 1 and 2 both land on the screen, mixed together." },
        { label: "3. > out.txt", says: "Stream 1 goes into a file. Problems still show on the screen." },
        { label: "4. 2> errors.txt", says: "Stream 2 goes into its own file: only the problems." },
        { label: "5. > all.txt 2>&1", says: "Stream 2 follows stream 1: everything in one file." },
      ]}
    />
  );
}

function LinuxPipe() {
  return (
    <SketchSteps
      title="a pipeline"
      intro="Press Play to follow the lines through four tools."
      label="awk prints the IP field of every line; sort puts equal addresses next to each other; uniq dash c squeezes each group into a count; sort dash rn puts the biggest count first; head keeps the top three"
      steps={[
        { label: "1. awk '{print $2}'", says: "400 log lines become 400 IP addresses." },
        { label: "2. sort", says: "Equal addresses now sit next to each other." },
        { label: "3. uniq -c", says: "Each group becomes one line with its count in front." },
        { label: "4. sort -rn", says: "Biggest count first." },
        { label: "5. head -3", says: "The top three. Every tool ran at the same time, passing lines along." },
      ]}
    />
  );
}

function LinuxPermissions() {
  return (
    <SketchSteps
      title="rwx, three times"
      intro="Press Play to read -rwxr-xr-x as a number."
      label="the first character is the type; then three letters for the owner, three for the group, three for everyone else; r is 4, w is 2, x is 1; add them per group to get 755"
      steps={[
        { label: "1. -rwxr-xr-x", says: "One type character, then three groups of three." },
        { label: "2. Owner: rwx", says: "4 + 2 + 1 = 7: read, write and run." },
        { label: "3. Group: r-x", says: "4 + 0 + 1 = 5: read and run." },
        { label: "4. Others: r-x", says: "4 + 0 + 1 = 5: read and run." },
        { label: "5. 755", says: "chmod 755 sets all nine at once. A private key wants 600: rw for you, nothing for others." },
      ]}
    />
  );
}

function LinuxSignals() {
  return (
    <SketchSteps
      title="TERM, wait, KILL"
      intro="Press Play to stop two programs properly."
      label="TERM is sent to both programs; the polite one cleans up and exits; the stubborn one ignores TERM; after a few seconds of waiting, KILL is sent; the kernel ends it at once, without any clean-up"
      steps={[
        { label: "1. pkill -TERM -x hogger", says: "Both programs are asked to finish." },
        { label: "2. The polite one", says: "Closes its files and exits cleanly." },
        { label: "3. The stubborn one", says: "Ignores TERM and keeps running." },
        { label: "4. Wait a few seconds", says: "pgrep -x hogger, every half second." },
        { label: "5. pkill -KILL -x hogger", says: "The kernel ends it on the spot. No clean-up, so KILL comes last." },
      ]}
    />
  );
}

function LinuxOpenFile() {
  return (
    <SketchSteps
      title="a name, the data, and an open file"
      intro="Press Play to see why rm does not free the space."
      label="a folder entry, the name, points at the file's data; the running app also holds the data open; rm removes the name but the app still holds the data, so the space stays used; truncate empties the data itself, and the space comes back"
      steps={[
        { label: "1. Name and data", says: "debug.log is a name in a folder, pointing at 620 KB of data." },
        { label: "2. The app holds it open", says: "The app writes into the data directly." },
        { label: "3. rm debug.log", says: "The name is gone. The app still holds the data: the space stays used." },
        { label: "4. truncate -s 0 instead", says: "The same file, emptied. The app keeps writing; the space is back at once." },
      ]}
    />
  );
}

function LinuxForLoop() {
  return (
    <SketchSteps
      title="one body, many files"
      intro="Press Play to watch the loop run."
      label="the glob makes a list of six file names; the loop takes the first name into the variable f and runs the body; then the next name, and the next; after the last name the loop ends"
      steps={[
        { label: "1. for f in captures/*.csv", says: "The shell makes the list: six names, in order." },
        { label: "2. First pass", says: "f is captures-2026-11-17.csv; the body runs." },
        { label: "3. Second pass", says: "f is captures-2026-11-18.csv; the same body runs again." },
        { label: "4. ... and so on", says: "One pass per name, whether there are six or six thousand." },
        { label: "5. done", says: "After the last name, the loop ends." },
      ]}
    />
  );
}

function LinuxEnv() {
  return (
    <SketchSteps
      title="copies go down"
      intro="Press Play to follow a variable from shell to child."
      label="the shell sets a variable; without export the child does not get it; after export, every child gets a copy; when the child changes its copy, the parent's value stays the same"
      steps={[
        { label: "1. colour=blue", says: "A variable in your shell only." },
        { label: "2. Start a child", says: "bash -c ... sees nothing: it was not exported." },
        { label: "3. export colour", says: "Now every program started from this shell gets a copy." },
        { label: "4. The child changes its copy", says: "Only the copy changes. Nothing ever travels back up to the parent." },
      ]}
    />
  );
}

function LinuxPorts() {
  return (
    <SketchSteps
      title="one address, many ports"
      intro="Press Play to connect to the right program."
      label="the machine has one address; port 22 leads to ssh, port 5432 to the database, port 8080 to the observatory app; a client names the address and the port; with nothing listening on a port, the connection is refused"
      steps={[
        { label: "1. One machine, one address", says: "127.0.0.1 when you talk to yourself." },
        { label: "2. Many listeners", says: "22: ssh. 5432: the database. 8080: the observatory app." },
        { label: "3. curl localhost:8080", says: "The address picks the machine; the port picks the program." },
        { label: "4. curl localhost:9999", says: "Nothing listens there: Connection refused, exit code 7." },
      ]}
    />
  );
}

function LinuxCron() {
  return (
    <SketchSteps
      title="five fields"
      intro="Press Play to read 30 2 * * * field by field."
      label="minute thirty; hour two; any day of the month; any month; any day of the week; so every day at two thirty in the morning; a job runs when all five fields match the clock"
      steps={[
        { label: "1. Minute: 30", says: "At half past." },
        { label: "2. Hour: 2", says: "Two in the morning (24-hour clock)." },
        { label: "3. Day of month: *", says: "Any day." },
        { label: "4. Month: *", says: "Any month." },
        { label: "5. Day of week: *", says: "Any day of the week. So: every day at 02:30. With 1 here instead, only Mondays." },
      ]}
    />
  );
}

function AiRequestFlow() {
  return (
    <SketchSteps
      title="one question's journey"
      intro="Press Play to follow a visitor's question to the model and back."
      label="the visitor asks atlas; the controller builds a prompt with chat client; spring ai sends it as json; the labbox gateway checks the budget and forwards it with the real key; the model writes an answer; it comes back the same way as text"
      steps={[
        { label: "1. GET /ask?q=...", says: "A visitor's browser calls Atlas." },
        { label: "2. ChatClient builds a prompt", says: "chat.prompt().user(q): the question becomes a user message." },
        { label: "3. Spring AI sends JSON", says: "A chat completions request, naming the model ai-chat." },
        { label: "4. The LabBox gateway", says: "Checks your budget, logs the call, adds the real key, forwards it." },
        { label: "5. The model answers", says: "Token by token, then the whole answer comes back as JSON." },
        { label: "6. .content()", says: "Spring AI hands your controller the text, and Atlas returns it." },
      ]}
    />
  );
}

function AiRoles() {
  return (
    <SketchSteps
      title="system, user, assistant"
      intro="Press Play to see who writes each message."
      label="the developer writes the system message with the rules; the visitor writes the user message; the model writes the assistant message, following both"
      steps={[
        { label: "1. system", says: "You, the developer: who Atlas is and its rules. Sent with every request." },
        { label: "2. user", says: "The visitor: Name one planet with rings." },
        { label: "3. assistant", says: "The model: Saturn is a planet with rings." },
        { label: "4. Next time", says: "The rules come first again: the model has no memory of its own." },
      ]}
    />
  );
}

function AiTemperature() {
  return (
    <SketchSteps
      title="picking the next word"
      intro="Press Play to see temperature at work."
      label="after the sky is, the candidates are blue with a high probability and clear and full with lower ones; at a low temperature the model almost always picks blue; at a high temperature it often picks a less likely word"
      steps={[
        { label: "1. The sky is ...", says: "Candidates: blue 70%, clear 10%, full 5%, and many more." },
        { label: "2. Temperature 0", says: "Almost always the top choice: blue, blue, blue." },
        { label: "3. Temperature 0.2", says: "Mostly the top choice, now and then another." },
        { label: "4. Temperature 1.5", says: "Less likely words often win: surprising, sometimes odd." },
      ]}
    />
  );
}

function AiStreaming() {
  return (
    <SketchSteps
      title="call versus stream"
      intro="Press Play to compare what the visitor sees."
      label="the model writes tokens one after another; with call the server waits for the last token and sends everything at once; with stream the server sends each token as soon as it exists"
      steps={[
        { label: "1. The model writes", says: "One token after another, for about two seconds." },
        { label: "2. With call()", says: "The screen stays empty until the last token, then everything appears." },
        { label: "3. With stream()", says: "The first words appear after about half a second." },
        { label: "4. Same total", says: "Same tokens, same price; only the empty wait is shorter." },
      ]}
    />
  );
}

function AiStructured() {
  return (
    <SketchSteps
      title="text in, a record out"
      intro="Press Play to follow entity(TourPlan.class)."
      label="spring ai writes the json schema of the record into the prompt; the model answers with json in that shape; jackson reads the json into a tourplan record; the controller returns it"
      steps={[
        { label: "1. entity(TourPlan.class)", says: "Spring AI looks at the record's fields." },
        { label: "2. The schema goes in the prompt", says: "title is a string; stops is a list of gallery and minutes." },
        { label: "3. The model answers in JSON", says: "Following the shape, with no explanations around it." },
        { label: "4. Jackson reads it", says: "The JSON becomes a TourPlan, ready for your Java code." },
      ]}
    />
  );
}

function AiMemory() {
  return (
    <SketchSteps
      title="a session, turn by turn"
      intro="Press Play to follow Ria's conversation."
      label="ria asks a first question; the session advisor stores it and the answer; her second question arrives; the advisor loads her session and sends the earlier turn with the new question; after many turns the session is compacted to its last turns"
      steps={[
        { label: "1. First question", says: "My name is Ria and I am 9. It goes to the model with the system prompt." },
        { label: "2. Stored", says: "The session keeps the question and the answer, under Ria's id." },
        { label: "3. Second question", says: "The advisor loads Ria's session and sends it before the new question." },
        { label: "4. Sam asks", says: "Sam's session is empty: nothing of Ria's travels with his question." },
        { label: "5. Compaction", says: "After more than 8 turns, only the last 4 stay in the view the model sees." },
      ]}
    />
  );
}

function AiToolCalling() {
  return (
    <SketchSteps
      title="a tool call"
      intro="Press Play to follow one question that needs a tool."
      label="the app sends the question and the tool descriptions; the model replies with a tool call instead of an answer; spring ai runs the java method; the result goes back to the model; the model answers with the real fact"
      steps={[
        { label: "1. Question and tools", says: "Is it open next Monday? plus the descriptions of today, nextDay, openingHours ..." },
        { label: "2. The model asks", says: "Not an answer: please run nextDay(MONDAY)." },
        { label: "3. Spring AI runs your method", says: "nextDay returns 2026-11-23 (MONDAY)." },
        { label: "4. Another round", says: "The model asks for openingHours(2026-11-23); it returns Closed." },
        { label: "5. The answer", says: "The museum is closed next Monday. Real facts, from your code." },
      ]}
    />
  );
}

function AiToolConfirmation() {
  return (
    <SketchSteps
      title="propose, then decide"
      intro="Press Play to follow a booking that waits for a yes."
      label="the model proposes a booking; the loop pauses before anything runs; the app shows the call to the visitor; the visitor says yes or no; a yes runs the tool, a no answers the model with a message; the model writes the final answer"
      steps={[
        { label: "1. The model proposes", says: "bookSeats(2026-11-28, 16:00, 2 seats)." },
        { label: "2. The loop pauses", says: "requiresConfirmation: nothing runs; the reply returns to the app." },
        { label: "3. The visitor decides", says: "The app shows the call: book 2 seats at 16:00?" },
        { label: "4a. Yes", says: "The tool runs: 2 seats booked. The result goes back to the model." },
        { label: "4b. No", says: "The tool does not run; the model gets the deny message instead." },
        { label: "5. The answer", says: "The model tells the visitor what really happened." },
      ]}
    />
  );
}

function AiToolContext() {
  return (
    <SketchSteps
      title="arguments and context"
      intro="Press Play to see what the model can and cannot set."
      label="the model fills the tool's arguments such as the date and seats; the app puts the visitor in the tool context; spring ai hands both to the tool; the model never sees the context and cannot change it"
      steps={[
        { label: "1. The model fills arguments", says: "date 2026-11-28, time 16:00, seats 2." },
        { label: "2. The app sets the context", says: "visitor = ria, from the login or the screen." },
        { label: "3. The tool gets both", says: "bookSeats(date, time, seats, context)." },
        { label: "4. Out of reach", says: "The model never sees the context: whatever it says, the booking is Ria's." },
      ]}
    />
  );
}

function AiAdvisorChain() {
  return (
    <SketchSteps
      title="the advisor chain"
      intro="Press Play to follow a call through two advisors."
      label="the request passes the usage advisor, then the language advisor, then reaches the model; the response comes back through the language advisor, then the usage advisor, which counts its tokens"
      steps={[
        { label: "1. call()", says: "The request enters the chain." },
        { label: "2. Usage advisor, on the way in", says: "Notes the time; passes the request on." },
        { label: "3. Language advisor", says: "Adds Answer in Marathi. to the system message." },
        { label: "4. The model", says: "Answers in Marathi." },
        { label: "5. On the way back", says: "The usage advisor counts the call and its tokens, then returns the answer." },
      ]}
    />
  );
}

function AiMcp() {
  return (
    <SketchSteps
      title="MCP in four messages"
      intro="Press Play to follow a client using Atlas's tools."
      label="the client sends initialize and learns the server's name; it sends tools list and learns four tools; its model decides to use planetarium shows; the client sends tools call and gets the result back"
      steps={[
        { label: "1. initialize", says: "Hello, I am a client. The server: I am atlas-museum, with tools." },
        { label: "2. tools/list", says: "today, nextDay, openingHours, planetariumShows, with descriptions." },
        { label: "3. The client's model decides", says: "This question needs planetariumShows for 2026-11-28." },
        { label: "4. tools/call", says: "Atlas runs its Java method and returns the shows as text." },
      ]}
    />
  );
}

function AiEmbeddings() {
  return (
    <SketchSteps
      title="texts become points"
      intro="Press Play to see meaning turn into numbers."
      label="each exhibit description goes into the embedding model and comes out as a list of 1536 numbers; similar descriptions land close together; a question is embedded the same way; the nearest point is the answer"
      steps={[
        { label: "1. A description goes in", says: "The Foucault pendulum: as the Earth rotates, its swing turns." },
        { label: "2. Numbers come out", says: "1,536 numbers: 0.003, 0.060, 0.051, ..." },
        { label: "3. Every exhibit gets a point", says: "Pendulum, prism, bicycle, Rajasaurus ... each at its own place." },
        { label: "4. The question too", says: "Which exhibit shows that the Earth spins? becomes a point." },
        { label: "5. The nearest wins", says: "Cosine similarity is highest for the pendulum: Foucault pendulum." },
      ]}
    />
  );
}

function AiVectorStore() {
  return (
    <SketchSteps
      title="embed once, search many times"
      intro="Press Play to follow the cards into the store."
      label="at start-up each card is embedded once and stored with its text and metadata; later a search embeds only the question; the store compares it with every stored vector and returns the closest above the threshold"
      steps={[
        { label: "1. Start-up", says: "CardLoader reads 12 cards into Documents, each with its file." },
        { label: "2. store.add", says: "Each card is embedded once; text, vector and file are kept together." },
        { label: "3. A search", says: "Where is the pendulum? Only the question is embedded." },
        { label: "4. Compare", says: "The store ranks every card by similarity to the question." },
        { label: "5. Filter", says: "topK 3, threshold 0.5: foucault-pendulum.md, 0.64. Nothing weaker." },
      ]}
    />
  );
}

function AiEtl() {
  return (
    <SketchSteps
      title="extract, transform, load"
      intro="Press Play to follow a card through the pipeline."
      label="the markdown reader turns each card into documents, one per heading, with the file in metadata; the token text splitter cuts them into chunks of about 100 tokens that keep the metadata; the chunks are added to the vector store"
      steps={[
        { label: "1. Extract", says: "MarkdownDocumentReader: visitor-information.md becomes 3 documents, one per heading." },
        { label: "2. Label", says: "Every document gets file = visitor-information.md." },
        { label: "3. Transform", says: "TokenTextSplitter cuts long documents into chunks of about 100 tokens." },
        { label: "4. Metadata follows", says: "Each chunk still knows its file." },
        { label: "5. Load", says: "vectorStore.add(chunks): 12 cards, 14 documents, 23 chunks." },
      ]}
    />
  );
}

function AiRag() {
  return (
    <SketchSteps
      title="retrieve, augment, generate"
      intro="Press Play to follow one question through RAG."
      label="the question is embedded and searched in the vector store; the three closest chunks above the threshold come back; the advisor adds them to the user message with instructions; the model answers from them; the app returns the answer with the files of the chunks"
      steps={[
        { label: "1. The question", says: "How much is a ticket for a child?" },
        { label: "2. Retrieve", says: "QuestionAnswerAdvisor searches the store: the ticket chunk, 0.40." },
        { label: "3. Augment", says: "The chunk is added to the user message, with: answer from the context." },
        { label: "4. Generate", says: "The model answers: 60 rupees for children aged 5 to 15." },
        { label: "5. Sources", says: "The retrieved chunks name their file: visitor-information.md." },
      ]}
    />
  );
}

function AiVision() {
  return (
    <SketchSteps
      title="a picture in a message"
      intro="Press Play to follow a visitor's photo."
      label="the visitor's photo is shrunk to fit 512 pixels; it is encoded as a data url; the question and the picture go in one user message; the model reads both and answers in text"
      steps={[
        { label: "1. The photo arrives", says: "pendulum.jpg, 800 by 600 pixels, from the visitor's phone." },
        { label: "2. Shrink it", says: "Photos.shrink: 512 by 384, one tile instead of four." },
        { label: "3. One message, two parts", says: "text: What is this exhibit? plus image: data:image/jpeg;base64,..." },
        { label: "4. The model looks", says: "It reads the picture as tokens, together with the words." },
        { label: "5. Words come back", says: "This exhibit looks like a Foucault pendulum." },
      ]}
    />
  );
}

function AiEvaluation() {
  return (
    <SketchSteps
      title="two ways to measure"
      intro="Press Play to see retrieval and answers measured."
      label="golden questions are searched and each hit is counted, with no model call; for an answer, a judge model reads the question, the retrieved cards and the answer, and says yes or no"
      steps={[
        { label: "1. Golden questions", says: "15 real questions, each with the card that must be found." },
        { label: "2. Measure retrieval", says: "Search each one: is its card in the top 3? Count the hits. No model, no cost." },
        { label: "3. A real answer", says: "Atlas answers a question from the cards." },
        { label: "4. The judge reads", says: "The question, the cards and the answer go to a second call." },
        { label: "5. The verdict", says: "YES or NO: relevant to the question and the cards?" },
      ]}
    />
  );
}

function AiGuardrails() {
  return (
    <SketchSteps
      title="guards before the model"
      intro="Press Play to follow three questions."
      label="a question passes the length limit and the privacy guard before it reaches the model; a long attack is refused by the limit; a phone number is refused by the privacy guard; neither reaches the model"
      steps={[
        { label: "1. A long attack", says: "336 characters of ignore all your instructions: the length limit refuses it." },
        { label: "2. A phone number", says: "my phone number is ...: the privacy guard answers with a kind reminder." },
        { label: "3. A normal question", says: "When do the shows start? passes both guards." },
        { label: "4. The model", says: "Only the third question reaches it, and costs tokens." },
      ]}
    />
  );
}

function AiCostMeter() {
  return (
    <SketchSteps
      title="where tokens are counted"
      intro="Press Play to follow one answer's tokens."
      label="the model replies with its usage; spring ai reads it into the response metadata; the controller turns tokens into dollars; spring ai records the same tokens in a metric that actuator shows"
      steps={[
        { label: "1. The reply", says: "The model's answer, with usage: tokens in and tokens out." },
        { label: "2. Metadata", says: "response.getMetadata().getUsage(): getPromptTokens(), getCompletionTokens()." },
        { label: "3. Dollars", says: "in times 0.15 per million, plus out times 0.60 per million." },
        { label: "4. Metrics", says: "Spring AI adds the same tokens to gen_ai.client.token.usage." },
        { label: "5. Dashboards", says: "/actuator/metrics today; Prometheus and Grafana in production." },
      ]}
    />
  );
}

function AiWorkflows() {
  return (
    <SketchSteps
      title="routing, and review loops"
      intro="Press Play to follow both workflows."
      label="a router call picks a desk, and a second call answers with that desk's prompt; a writer drafts a label, a reviewer checks it against rules, and the writer rewrites with the feedback until approved or three drafts"
      steps={[
        { label: "1. Route", says: "Are you open on Sunday? The router says VISIT." },
        { label: "2. Answer as that desk", says: "The front desk prompt, with the real hours, answers." },
        { label: "3. Draft", says: "The writer drafts a label for the prism room." },
        { label: "4. Review", says: "Too long: cut it to 40 words." },
        { label: "5. Rewrite, review again", says: "Approved on draft 2. At most 3 drafts, so the loop always ends." },
      ]}
    />
  );
}

function AiAtlasLive() {
  return (
    <SketchSteps
      title="all of Atlas in one call"
      intro="Press Play to follow one message on the lobby screen."
      label="a message passes the length limit and the privacy guard, the session adds the visitor's conversation, retrieval adds the closest cards, the model may call tools, and the answer returns with its sources"
      steps={[
        { label: "1. Guards", says: "Length limit, then the privacy guard." },
        { label: "2. Memory", says: "Ria's last turns are added from her session." },
        { label: "3. Retrieval", says: "The 3 closest card chunks are added to her question." },
        { label: "4. The model, with tools", says: "It may ask for openingHours or planetariumShows." },
        { label: "5. The reply", says: "The answer, and the cards it came from." },
      ]}
    />
  );
}

function L4jAiCircles() {
  return (
    <SketchNested
      title="circles inside circles"
      intro="Press Play to go from the biggest circle to the smallest."
      label="artificial intelligence contains machine learning, which contains deep learning, which contains generative AI; a large language model sits in the smallest circle"
      steps={[
        { label: "Artificial intelligence", says: "Any program doing something we would call intelligent: even hand-written rules." },
        { label: "Machine learning", says: "The rule is learned from examples, not written: like the 12-minute threshold." },
        { label: "Deep learning", says: "Machine learning with neural networks of many layers." },
        { label: "Generative AI", says: "Deep learning models that create new text, images or code." },
        { label: "LLM", says: "A large language model lives in the smallest circle: it is all four at once." },
      ]}
    />
  );
}

function L4jNeuron() {
  return (
    <SketchSteps
      title="one neuron deciding"
      intro="Press Play to follow one morning's prediction."
      label="the inputs rain, holiday and track work are multiplied by their weights, added together with the bias, and the neuron fires if the total is above zero"
      steps={[
        { label: "1. Inputs", says: "Rain 0, holiday 1, track work 1." },
        { label: "2. Times the weights", says: "0 x 0.1, 1 x 0.2, 1 x 0.3: each input counts as much as its weight says." },
        { label: "3. Add the bias", says: "0 + 0.2 + 0.3 - 0.2 = 0.3." },
        { label: "4. Fire or not", says: "0.3 is above zero: the neuron says 1, late." },
        { label: "5. Learning", says: "If it was wrong, training nudges each weight a little and tries again." },
      ]}
    />
  );
}

function L4jContextWindow() {
  return (
    <SketchSteps
      title="a window that slides"
      intro="Press Play to watch a chat grow past the window."
      label="messages arrive one after another; while they fit in the token budget the model sees them all; when a new message arrives the oldest falls out of the window"
      steps={[
        { label: "1. A short chat", says: "Three messages, 45 tokens: all inside the window." },
        { label: "2. It grows", says: "Every new message is added at the end." },
        { label: "3. Over the budget", says: "The total passes the budget: something has to go." },
        { label: "4. The oldest falls out", says: "Travelling with my grandmother next Sunday is no longer sent." },
        { label: "5. What the model sees", says: "Only the newest messages that fit, oldest first." },
      ]}
    />
  );
}

function L4jEmbeddingSpace() {
  return (
    <SketchSteps
      title="search by meaning"
      intro="Press Play to follow one passenger's question."
      label="each text becomes a vector of 384 numbers; vectors with similar meaning point in similar directions; the question is compared with every FAQ question and the closest wins"
      steps={[
        { label: "1. Embed the question", says: "How heavy can my suitcase be? becomes 384 numbers." },
        { label: "2. Embed the FAQ", says: "Every FAQ question becomes 384 numbers too, by the same model." },
        { label: "3. Compare directions", says: "Cosine similarity of the question with each FAQ question." },
        { label: "4. Rank", says: "How much baggage can I carry? scores highest." },
        { label: "5. Answer", says: "Return that entry's answer: 40 kg free." },
      ]}
    />
  );
}

function L4jAttention() {
  return (
    <SketchSteps
      title="what does it attend to"
      intro="Press Play to follow attention for one word."
      label="the query of it is compared with the key of every word by a dot product; the scores are divided by the square root of the vector length; softmax turns them into weights; the train gets the most attention"
      steps={[
        { label: "1. A query", says: "The word it asks: who here moves on a schedule?" },
        { label: "2. Compare with keys", says: "Dot product of the query with the key of train, station and it." },
        { label: "3. Scale", says: "Divide each score by the square root of 3, the vector length." },
        { label: "4. Softmax", says: "Scores become weights that add up to 1." },
        { label: "5. The answer", says: "train 0.46, it 0.36, station 0.18: it mostly means the train." },
      ]}
    />
  );
}

function L4jLlmPipeline() {
  return (
    <SketchSteps
      title="how an LLM answers"
      intro="Press Play to follow one question through the model."
      label="the question is split into tokens; each token becomes an embedding; layers of attention refine them; the last layer scores every possible next token; softmax with temperature picks one; the token is added and the loop repeats"
      steps={[
        { label: "1. Tokens", says: "When does the Ghat Express leave Pune? becomes 9 tokens." },
        { label: "2. Embeddings", says: "Each token becomes a vector of numbers." },
        { label: "3. Layers", says: "Attention and neurons, dozens of layers, refine every vector." },
        { label: "4. Scores", says: "One score for each of about 200,000 possible next tokens." },
        { label: "5. Pick one", says: "Softmax and temperature, then a weighted draw: The." },
        { label: "6. Repeat", says: "Add the token, run the model again, until the answer ends." },
      ]}
    />
  );
}

function L4jHttpCall() {
  return (
    <SketchSteps
      title="one call to a model"
      intro="Press Play to follow Setu's first question."
      label="Setu builds a JSON body with the model and the messages, posts it with its key to the LabBox gateway, the gateway checks the budget and forwards it to OpenAI, and the JSON answer comes back the same way"
      steps={[
        { label: "1. Build the body", says: "model ai-chat, a system message, the passenger's question." },
        { label: "2. POST with a key", says: "Authorization: Bearer and the key; Content-Type: application/json." },
        { label: "3. The gateway", says: "Checks the key and the daily budget, logs the call, adds the real OpenAI key." },
        { label: "4. The model", says: "gpt-4o-mini reads 62 tokens and writes 45, one at a time." },
        { label: "5. The answer", says: "choices[0].message.content, plus usage: what it cost." },
      ]}
    />
  );
}

function L4jAiService() {
  return (
    <SketchSteps
      title="inside an AI Service"
      intro="Press Play to follow one call to setu.chat."
      label="the call goes to a proxy; the proxy reads the annotations, builds the system and user messages, calls the ChatModel, and converts the answer to the method's return type"
      steps={[
        { label: "1. Your code", says: 'setu.chat("Hello!") on the Assistant interface.' },
        { label: "2. The proxy", says: "A class the JDK generated at run time receives the call." },
        { label: "3. Annotations", says: '@SystemMessage(fromResource = "setu-system.txt") becomes the system message.' },
        { label: "4. Messages", says: "The argument becomes the user message; memory adds the history." },
        { label: "5. The model", says: "ChatModel.chat(...) sends the request through the gateway." },
        { label: "6. Return type", says: "String here; a record, an enum or a TokenStream in later chapters." },
      ]}
    />
  );
}

function L4jToolCall() {
  return (
    <SketchSteps
      title="a tool call, step by step"
      intro="Press Play to follow one question that needs Java."
      label="the question goes to the model with the tool descriptions; the model asks for nextDate and fare; LangChain4j runs the Java methods; the results go back; the model answers"
      steps={[
        { label: "1. Question and tools", says: "3 tickets to Karjat this Saturday? plus the descriptions of fare and nextDate." },
        { label: "2. The model asks", says: "No text: two tool calls, nextDate(SATURDAY) and fare(Karjat)." },
        { label: "3. Java runs", says: "LangChain4j calls RailTools: 2026-11-28 and 140." },
        { label: "4. Results go back", says: "Two tool messages are added to the conversation." },
        { label: "5. The answer", says: "Saturday 28 November, three tickets for Rs 420." },
      ]}
    />
  );
}

function L4jRag() {
  return (
    <SketchSteps
      title="retrieval-augmented generation"
      intro="Press Play to follow indexing, then one question."
      label="documents are loaded, split into pieces, embedded and stored once; a question is embedded, the closest pieces are found, and they travel to the model with the question"
      steps={[
        { label: "1. Load", says: "Five rule documents from the docs folder." },
        { label: "2. Split", says: "Pieces of at most 300 characters, overlapping by 30." },
        { label: "3. Embed and store", says: "Each piece becomes 1,536 numbers, kept with its text and file name." },
        { label: "4. A question", says: "Can I bring my guitar? is embedded too." },
        { label: "5. Retrieve", says: "The closest piece above 0.7: Musical instruments up to 1.5 metres travel free." },
        { label: "6. Generate", says: "The model answers from that piece, and only from it." },
      ]}
    />
  );
}

function L4jSequence() {
  return (
    <SketchSteps
      title="two agents in a sequence"
      intro="Press Play to follow one message through the help desk."
      label="a message goes into the scope; the classifier reads it and writes topic; the writer reads message and topic and writes reply; the workflow returns reply"
      steps={[
        { label: "1. handle(message)", says: "The workflow puts message into a new agentic scope." },
        { label: "2. Classifier", says: "Reads message, answers COMPLAINT, and writes it to the scope as topic." },
        { label: "3. Writer", says: "Reads message and topic from the scope." },
        { label: "4. Reply", says: "Writes a kind first reply to the scope as reply." },
        { label: "5. Return", says: "The workflow returns reply: two model calls, one method call." },
      ]}
    />
  );
}

function L4jWorkflow() {
  return (
    <SketchSteps
      title="classify, route, review"
      intro="Press Play to follow a timetable question."
      label="the classifier writes topic; a condition sends the message to the timetable desk; the scorer rates the reply; below 0.8 the editor rewrites it and the scorer rates it again"
      steps={[
        { label: "1. Classify", says: "When does the Monsoon Mail reach Karjat? becomes topic TIMETABLE." },
        { label: "2. Route", says: "Only the condition topic == TIMETABLE is true, so only the timetable desk runs." },
        { label: "3. Answer", says: "The desk writes reply from the facts: 18:40." },
        { label: "4. Score", says: "The scorer rates the reply below 0.8." },
        { label: "5. Edit", says: "The editor rewrites reply: shorter, no promises." },
        { label: "6. Score again", says: "0.8 or more: the loop exits. Never more than 3 rounds." },
      ]}
    />
  );
}

function L4jStreaming() {
  return (
    <SketchSteps
      title="one streamed answer"
      intro="Press Play to follow the real run from this chapter."
      label="the request goes out; the first piece arrives after 905 milliseconds and onPartialResponse prints it; 56 pieces follow; onCompleteResponse runs after 2103 milliseconds"
      steps={[
        { label: "1. 0 ms: request", says: "Setu sends the question with stream: true; the HTTP response stays open." },
        { label: "2. 905 ms: first piece", says: "data: [Tr] arrives; onPartialResponse prints it. The passenger starts reading." },
        { label: "3. Piece after piece", says: "[ains] [ slow] [ down]... each one printed as it comes, 56 in all." },
        { label: "4. 2103 ms: [DONE]", says: "onCompleteResponse gets the whole ChatResponse, with its token usage." },
        { label: "5. Without streaming", says: "The same answer, but an empty box until 2103 ms." },
      ]}
    />
  );
}

function L4jMemoryWindow() {
  return (
    <SketchSteps
      title="a sliding window of messages"
      intro="Press Play to follow one conversation."
      label="each question and answer is added to the memory; every call sends the whole memory; when the window is full the oldest messages are evicted, but the system message stays"
      steps={[
        { label: "1. First question", says: "The memory holds the system message and Meera's question; both go to the model." },
        { label: "2. First answer", says: "Setu's answer is added: the next call sends all three." },
        { label: "3. More questions", says: "Every call sends the whole memory again, so every remembered token is paid for again." },
        { label: "4. The window is full", says: "With maxMessages(10), the next message pushes out the oldest one." },
        { label: "5. Always kept", says: "The system message is never evicted: Setu never forgets who it is." },
      ]}
    />
  );
}

function L4jMcp() {
  return (
    <SketchSteps
      title="an MCP client and a stdio server"
      intro="Press Play to follow chapter 20's client."
      label="the Java client starts the server as a child process, they shake hands over standard input and output, the client lists the tools, and calls one when the model asks"
      steps={[
        { label: "1. Start", says: "Building DefaultMcpClient starts mcp-server-filesystem as a child process." },
        { label: "2. Handshake", says: "initialize, as JSON-RPC 2.0 messages over its standard input and output." },
        { label: "3. tools/list", says: "The server describes its 14 tools; McpToolProvider turns them into LangChain4j tools." },
        { label: "4. The model asks", says: "It wants read_text_file for a notice: the client sends tools/call." },
        { label: "5. The answer", says: "The server reads the file, only inside its folder, and returns the text." },
        { label: "6. Close", says: "Closing the client stops the server process." },
      ]}
    />
  );
}

function L4jVectorSearch() {
  return (
    <SketchSteps
      title="one search in the embedding store"
      intro="Press Play to follow the bicycle question."
      label="the question is embedded, compared with every stored card, scored as cosine plus one over two, and only scores of at least 0.7 are kept"
      steps={[
        { label: "1. Embed the question", says: "Can I take my bicycle? becomes 1,536 numbers." },
        { label: "2. Compare", says: "The store measures how close it is to every card's vector." },
        { label: "3. Score", says: "LangChain4j's score is (cosine + 1) / 2: Luggage 0.712, Lost property 0.645, Pets 0.612." },
        { label: "4. Threshold", says: "minScore(0.7) keeps only Luggage: the right card." },
        { label: "5. No answer here", says: "What is the capital of France? Best score 0.543: nothing is returned." },
      ]}
    />
  );
}

function L4jGuardrails() {
  return (
    <SketchSteps
      title="guardrails around one call"
      intro="Press Play to follow two questions."
      label="the input guardrail checks the question before the model; a question over 300 characters is refused and never reaches the model; the output guardrail rewrites the answer before it is returned"
      steps={[
        { label: "1. setu.chat(question)", says: "Your method is called." },
        { label: "2. Input guardrail", says: "QuestionLimit: 111 characters, success(). The question goes on." },
        { label: "3. The model", says: "It writes: ... passenger Ravi, mobile 98220 12345, ..." },
        { label: "4. Output guardrail", says: "NoPhoneNumbers: successWith(...), the number becomes [number removed]." },
        { label: "5. The answer returns", says: "No extra model call; the passenger never sees the number." },
        { label: "6. A 379-character question", says: "fatal(TOO_LONG): InputGuardrailException, and no token is paid for." },
      ]}
    />
  );
}

function L4jSupervisor() {
  return (
    <SketchSteps
      title="a supervisor plans, step by step"
      intro="Press Play to follow the real run from this chapter."
      label="the planner reads the request and the agents' descriptions, calls the date agent, then the fare agent, then answers done with a summary"
      steps={[
        { label: "1. The request", says: "2 adults, Pune to Ratnagiri, next Sunday: the date and the total fare?" },
        { label: "2. Plan", says: "The planner reads the agents' names and descriptions and picks the date agent." },
        { label: "3. Date agent", says: "Its tool answers 2026-11-29." },
        { label: "4. Plan again", says: "With that result, the planner picks the fare agent for Ratnagiri." },
        { label: "5. Fare agent", says: "Its tool answers 420: the fare for one adult." },
        { label: "6. Done", says: "The planner writes the summary. With CONTEXT it multiplies: 2 x 420 = 840." },
      ]}
    />
  );
}

function LcNextToken() {
  return (
    <SketchSteps
      title="how a model writes an answer"
      intro="Press Play to follow the first words of an answer."
      label="the model reads the whole text so far, scores every possible next token, softmax turns the scores into probabilities, one token is picked and added, and the loop runs again"
      steps={[
        { label: "1. Read everything so far", says: "The system message, the question, and the answer written so far." },
        { label: "2. Attention", says: "Every token looks at every other token to work out the meaning." },
        { label: "3. Score every token", says: "About 200,000 scores, one for each piece in the vocabulary." },
        { label: "4. Softmax", says: "The scores become probabilities; temperature 0 makes the top one win." },
        { label: "5. Pick and add", says: "Today is added to the answer." },
        { label: "6. Again", says: "The loop runs once per output token, until the model chooses to stop." },
      ]}
    />
  );
}

function LcChatRequest() {
  return (
    <SketchSteps
      title="one chat request, there and back"
      intro="Press Play to follow Navin's first question."
      label="Python posts the model name and messages with a lab token; the gateway checks it and calls OpenAI with the real key; the answer and the token usage come back as JSON"
      steps={[
        { label: "1. Python builds JSON", says: "model ai-chat, a system message, and the member's question." },
        { label: "2. POST with a token", says: "To OPENAI_BASE_URL/chat/completions, with Authorization: Bearer and the lab token." },
        { label: "3. The gateway", says: "Checks the token and the budget, adds max_tokens 1024, and calls OpenAI with the real key." },
        { label: "4. The model", says: "gpt-4o-mini writes the answer, one token at a time." },
        { label: "5. JSON comes back", says: "choices[0].message.content holds the answer; usage says 61 in, 38 out." },
      ]}
    />
  );
}

function LcAiCircles() {
  return (
    <SketchNested
      title="circles inside circles"
      intro="Press Play to go from the biggest circle to the smallest."
      label="artificial intelligence contains machine learning, which contains deep learning, which contains generative AI; a large language model sits in the smallest circle"
      steps={[
        { label: "Artificial intelligence", says: "Any program doing something we would call intelligent: even Navin's hand-written rules." },
        { label: "Machine learning", says: "The rule is learned from examples, not written: like the 8 mm rain threshold." },
        { label: "Deep learning", says: "Machine learning with neural networks of many layers: telling a healthy grape leaf from a diseased one." },
        { label: "Generative AI", says: "Deep learning models that create new text, images or code." },
        { label: "LLM", says: "A large language model lives in the smallest circle: it is all four at once." },
      ]}
    />
  );
}

function LcAgentLoop() {
  return (
    <SketchSteps
      title="one agent run, step by step"
      intro="Press Play to follow chapter 10's question."
      label="the model receives the question and the tool descriptions, asks for two tools, Python runs them, the results go back, and the model answers"
      steps={[
        { label: "1. Question and tools", says: "The onion rate, and 60 crates for 10 days? Plus the descriptions of mandi_price and storage_cost." },
        { label: "2. The model asks", says: "No text: two tool calls, mandi_price(onion) and storage_cost(60, 10)." },
        { label: "3. Python runs them", says: "1850 from the rate table, 1200 from 60 x 10 x 2." },
        { label: "4. Results go back", says: "Two ToolMessages, each with the id of the call it answers." },
        { label: "5. The answer", says: "One more model call turns two numbers into a sentence. No tool calls: stop." },
      ]}
    />
  );
}

function LcMemoryThreads() {
  return (
    <SketchSteps
      title="a checkpointer and two threads"
      intro="Press Play to follow Ravi and Asha."
      label="each message is added to its thread's saved state; the model receives that thread's whole conversation; another thread starts empty"
      steps={[
        { label: "1. Ravi, thread M-104", says: "I am Ravi, 40 crates of onions. Saved under M-104." },
        { label: "2. Ravi again", says: "How much for 15 days? The model receives Ravi's whole thread, so them means 40 crates." },
        { label: "3. Asha, thread M-221", says: "The same words, but her thread is empty: the model asks how many crates." },
        { label: "4. Ravi a third time", says: "What is my name? His thread still holds it." },
      ]}
    />
  );
}

function LcRag() {
  return (
    <SketchSteps
      title="agentic RAG, one question"
      intro="Press Play to follow the storage question."
      label="the rule book was loaded, split and embedded once; for a question the model calls search_rules, the closest chunks above the threshold come back with their sources, and the model answers from them"
      steps={[
        { label: "1. Once, at start", says: "Five rule files loaded, split into 12 chunks, each embedded and stored." },
        { label: "2. The question", says: "Can I store 80 crates of onions? reaches the agent." },
        { label: "3. The model searches", says: "It calls search_rules with the whole question as the query." },
        { label: "4. The store", says: "The question is embedded; chunks scoring at least 0.3 come back, best first." },
        { label: "5. With sources", says: "Each piece starts with its file, like [storage.txt]." },
        { label: "6. The answer", says: "The model answers only from those pieces, and names the file." },
      ]}
    />
  );
}

function LcMcp() {
  return (
    <SketchSteps
      title="Navin and an MCP server"
      intro="Press Play to follow chapter 21's question."
      label="the adapter starts the server, lists its tools, the agent calls a tool over MCP, the server runs Python and answers, and the server stops at the end"
      steps={[
        { label: "1. Start", says: "MCPAdapter starts coop_server.py as a child process (stdio)." },
        { label: "2. List", says: "The server describes mandi_price and storage_cost; they become LangChain tools." },
        { label: "3. The model asks", says: "storage_cost with crates 15 and days 4." },
        { label: "4. Over MCP", says: "The adapter sends the call to the server; the server runs Python: 120." },
        { label: "5. The answer", says: "The result goes back to the model, which writes the reply." },
        { label: "6. Stop", says: "Leaving async with closes the connection and stops the server." },
      ]}
    />
  );
}

function LcMiddleware() {
  return (
    <SketchSteps
      title="middleware around one agent run"
      intro="Press Play to follow one run through chapter 22's middleware."
      label="before the agent starts, guards run; before each model call, the summarizer and the call limit; the model is called; around each tool call, the tool-error handler; then the loop continues until the answer"
      steps={[
        { label: "1. before_agent", says: "Guards run once, before anything else (chapter 24's length guard)." },
        { label: "2. before_model", says: "SummarizationMiddleware shortens a long thread; ModelCallLimitMiddleware counts calls." },
        { label: "3. The model", says: "Called with the prepared messages; it asks for mandi_price twice." },
        { label: "4. wrap_tool_call", says: "ToolErrorMiddleware runs each tool: 1850, and garlic's ValueError becomes a message." },
        { label: "5. Again", says: "before_model, then the model writes the answer from both results." },
        { label: "6. after_agent", says: "The run ends; hooks here could check what was written." },
      ]}
    />
  );
}

function LcHumanLoop() {
  return (
    <SketchSteps
      title="a booking waits for the manager"
      intro="Press Play to follow Ravi's booking."
      label="the model asks for book_storage, the middleware pauses the run and saves it, the manager decides, and the same thread resumes"
      steps={[
        { label: "1. The member asks", says: "Please book 80 crates of onions for 10 days." },
        { label: "2. The model asks", says: "book_storage with crates 80, days 10, crop onion." },
        { label: "3. Pause", says: "HumanInTheLoopMiddleware stops before the tool runs; the checkpointer saves the thread." },
        { label: "4. The manager", says: "Sees the request and decides: approve, edit (50 crates) or reject." },
        { label: "5. Resume", says: "Command(resume=...) on the same thread: the tool runs, or the model hears why not." },
        { label: "6. The answer", says: "Navin tells the member what was booked." },
      ]}
    />
  );
}

function LgRun() {
  return (
    <SketchSteps
      title="One complaint through Harsh's first graph"
      intro="Press Play to follow the state from START to END."
      label="Graph run"
      steps={[
        { label: "START", says: "The state is {'text': 'Pipe burst near the school'}. Nothing else is known yet." },
        { label: "classify", says: "The node reads the text and returns an update: {'kind': 'leak'}." },
        { label: "Merge", says: "LangGraph merges the update into the state: now text and kind." },
        { label: "write_reply", says: "The next node reads kind, looks up the promised hours, and returns {'reply': ...}." },
        { label: "Merge", says: "The state now holds text, kind and reply." },
        { label: "END", says: "invoke returns the final state; stream had shown each update as it happened." },
      ]}
    />
  );
}

function LgReducer() {
  return (
    <SketchSteps
      title="Two updates, one field"
      intro="Press Play to see how the reducer joins each update."
      label="Reducers"
      steps={[
        { label: "Start", says: "The state holds the text of a complaint about brown water near the hospital." },
        { label: "classify", says: "Returns severity 'urgent' and log ['classify: dirty_water']. The state is empty, so both are taken." },
        { label: "check_location", says: "Returns severity 'high' and log ['check_location: near a hospital or school']." },
        { label: "log", says: "operator.add joins old and new: the log now has both lines, in order." },
        { label: "severity", says: "higher('urgent', 'high') keeps the more serious value: urgent stays." },
        { label: "Without reducers", says: "The later update would win: the log would lose a line, and urgent would drop to high." },
      ]}
    />
  );
}

function LgRoute() {
  return (
    <SketchSteps
      title="A street spelt wrong, and the way out"
      intro="Press Play to follow 'Gandi Chowk' through the loop."
      label="Branch and loop"
      steps={[
        { label: "find_zone", says: "Try 1 uses the street as written. Not on the map: zone is empty, tries is 1." },
        { label: "after_find_zone", says: "No zone, and 1 is less than MAX_TRIES (2): go back to find_zone." },
        { label: "find_zone", says: "Try 2 uses the corrected spelling 'gandhi chowk': North zone, tries is 2." },
        { label: "after_find_zone", says: "A zone was found: go to route." },
        { label: "choose_team", says: "The kind is dirty_water: go to health_team." },
        { label: "Shivaji Path", says: "Never found: after 2 tries, after_find_zone sends it to ask_citizen. The limit is the way out." },
      ]}
    />
  );
}

function LgModelNode() {
  return (
    <SketchSteps
      title="Inside the triage node"
      intro="Press Play to see a model call become a state update."
      label="Model node"
      steps={[
        { label: "State in", says: "The node gets the state: text 'pani nahi aaya aaj gandhi chowk mein'." },
        { label: "Messages", says: "It builds a system message (the TRIAGE rules) and a human message (the complaint)." },
        { label: "Model", says: "with_structured_output(Triage) asks the model for exactly the Triage fields." },
        { label: "Validation", says: "kind and severity must be one of the Literal values, or the call fails here." },
        { label: "Update out", says: "model_dump() turns Triage into {'kind': 'no_water', 'severity': 'high', 'street': 'Gandhi Chowk'}." },
        { label: "Graph", says: "The graph merges it and routes on kind, as with any other node." },
      ]}
    />
  );
}

function LgJoin() {
  return (
    <SketchSteps
      title="Two lookups at once, then a join"
      intro="Press Play to watch the super-steps."
      label="Parallel"
      steps={[
        { label: "Step 1", says: "START has two edges: zone_lookup and history_lookup both run in this step." },
        { label: "Updates", says: "zone_lookup writes zone; history_lookup writes past. Different keys, so no conflict." },
        { label: "Join", says: "assign is behind the list edge [zone_lookup, history_lookup]: it waits for both." },
        { label: "Step 2", says: "assign runs once, with zone 'South' and 6 past complaints: a crew and a survey of the old main." },
        { label: "Same key?", says: "If both branches wrote the same key in one step, that key would need a reducer." },
      ]}
    />
  );
}

function LgSend() {
  return (
    <SketchSteps
      title="A storm night: map, then reduce"
      intro="Press Play to follow five complaints through Send."
      label="Send"
      steps={[
        { label: "fan_out", says: "Reads complaints (5 texts) and returns five Send('triage_one', {'text': ...})." },
        { label: "Map", says: "Five triage_one runs start in the same step, each with only its own text." },
        { label: "Reduce", says: "Each returns {'tickets': [ticket]}; operator.add collects all five into one list." },
        { label: "summarise", says: "Runs once, after all five: '5 complaints, 1 urgent'." },
        { label: "plan", says: "For each repair, returns a Command: goto engineer_approval over Rs 50,000, otherwise schedule." },
        { label: "The gap", says: "plan looks only at cost, so urgent dirty water was scheduled for tomorrow." },
      ]}
    />
  );
}

function LgThreads() {
  return (
    <SketchSteps
      title="Two phones, two threads"
      intro="Press Play to follow three WhatsApp messages."
      label="Threads"
      steps={[
        { label: "98220 writes", says: "invoke with thread_id 98220. The checkpointer has nothing for it yet: the state starts empty." },
        { label: "Run and save", says: "The message and Harsh's answer are added, and the thread is saved: 2 messages." },
        { label: "Process ends", says: "Everything in memory is gone. harsh.db still holds thread 98220." },
        { label: "98220 again", says: "A new process loads thread 98220 from the file, adds the new message: the model sees all 3." },
        { label: "Saved again", says: "The thread now holds 4 messages." },
        { label: "70300 writes", says: "Another thread_id: nothing saved for it, so it starts empty, and sees nothing of 98220." },
      ]}
    />
  );
}

function LgSummary() {
  return (
    <SketchSteps
      title="Folding old messages into a summary"
      intro="Press Play to watch the state stay small."
      label="Summary"
      steps={[
        { label: "Turns 1 to 3", says: "The state grows: 2, 4, 6 messages. Not more than 6 yet, so no summary." },
        { label: "Turn 4", says: "respond answers with 7 messages in front of it; now there are 8, more than 6." },
        { label: "summarise", says: "The model turns the first 6 messages into a short summary." },
        { label: "RemoveMessage", says: "Those 6 messages are removed from the state by id: 2 are kept." },
        { label: "Turn 5", says: "respond sends the summary in its system message, plus the few messages left." },
        { label: "Turn 6", says: "Asked for the address, the model finds it in the summary." },
      ]}
    />
  );
}

function LgDurable() {
  return (
    <SketchSteps
      title="A crash, and a resume that does only what is left"
      intro="Press Play to follow job J-102."
      label="Durable run"
      steps={[
        { label: "book_crew", says: "Runs, writes 'crew booked', and the checkpoint is saved." },
        { label: "order_parts", says: "Runs, writes 'parts ordered, Rs 18,000', and the checkpoint is saved." },
        { label: "notify_citizen", says: "The SMS gateway times out. The retry policy waits 0.5 s, then 1 s: three attempts in all." },
        { label: "Crash", says: "All three failed: invoke raises the error. The thread is saved with next = notify_citizen." },
        { label: "Resume", says: "Later, invoke(None, config) loads the thread and runs only notify_citizen." },
        { label: "Record", says: "One crew, one parts order, one SMS. Starting over would have booked both again." },
      ]}
    />
  );
}

function LgInterrupt() {
  return (
    <SketchSteps
      title="A repair that waits for the engineer"
      intro="Press Play to follow J-201 through two processes."
      label="Interrupt"
      steps={[
        { label: "write_brief", says: "The model writes a two-sentence brief. Rs 65,000 is over 50,000: go to approval." },
        { label: "interrupt", says: "approval calls interrupt({...}). The run stops, the thread is saved with next = approval." },
        { label: "Returned", says: "invoke returns the state with __interrupt__: the job, the estimate and the brief for the engineer." },
        { label: "Next morning", says: "A new process calls invoke(Command(resume={'approve': True, ...}), same thread_id)." },
        { label: "approval again", says: "The node runs from its first line; this time interrupt returns her answer." },
        { label: "schedule", says: "approved is true: the repair is scheduled, with her note." },
      ]}
    />
  );
}

function LgFork() {
  return (
    <SketchSteps
      title="Correcting a step, and the branch it makes"
      intro="Press Play to follow complaint C-311."
      label="Time travel"
      steps={[
        { label: "First run", says: "triage says 'other', route picks the repair crew, reply promises 72 hours. Checkpoints at every step." },
        { label: "History", says: "get_state_history lists them, newest first. The one with next = ('route',) holds triage's answer." },
        { label: "update_state", says: "Write kind dirty_water and severity urgent there, as triage: a new checkpoint, source 'update'." },
        { label: "invoke(None)", says: "From the new checkpoint, route runs again: health team. Then reply: 4 hours." },
        { label: "Two branches", says: "The old steps with 'other' are still in the history; the newest checkpoint is the corrected one." },
      ]}
    />
  );
}

function LgStore() {
  return (
    <SketchSteps
      title="One fact, many threads"
      intro="Press Play to follow phone 98220."
      label="Store"
      steps={[
        { label: "complaint-1", says: "'Please reply in Marathi from now on.' note_preferences asks the model: language = Marathi." },
        { label: "put", says: "store.put(('citizens', '98220'), 'profile', {'language': 'Marathi'}): outside the thread." },
        { label: "respond", says: "Reads the profile and replies in Marathi." },
        { label: "complaint-2", says: "A new thread, nothing about language in it. respond reads the same profile: Marathi again." },
        { label: "70300", says: "Another phone: no profile in the store, so English." },
      ]}
    />
  );
}

function LgAgentLoop() {
  return (
    <SketchSteps
      title="The agent loop, by hand"
      intro="Press Play to follow '98220' through the loop."
      label="Agent loop"
      steps={[
        { label: "agent", says: "The model reads the chat and the tool descriptions, and asks for find_tickets(phone='98220')." },
        { label: "should_continue", says: "The last message has tool_calls: go to tools." },
        { label: "tools", says: "ToolNode runs find_tickets and adds a ToolMessage: T-4471 and T-4475." },
        { label: "agent", says: "The model reads the result and asks for ticket_status twice, in one message." },
        { label: "tools", says: "Both calls run together; two ToolMessages come back." },
        { label: "agent", says: "Now it has the facts and answers, with no tool calls." },
        { label: "END", says: "should_continue sees no tool_calls: the run ends with the answer." },
      ]}
    />
  );
}

function LgReflection() {
  return (
    <SketchSteps
      title="Draft, check, and three exits"
      intro="Press Play to follow 'Can my children drink the tap water now?'."
      label="Reflection"
      steps={[
        { label: "agent", says: "Looks up the tickets and drafts an answer that says 'tomorrow morning' and gives advice." },
        { label: "check", says: "The model labels each sentence; Python keeps the new_claim ones: two problems." },
        { label: "Round 1", says: "Command(goto='agent') with the checker's feedback; rounds becomes 1." },
        { label: "Rewrite", says: "The advice is gone, but 'tomorrow' is still there. Checked again: round 2." },
        { label: "Round 3", says: "Still 'tomorrow'. Rounds is now over MAX_ROUNDS." },
        { label: "hand_over", says: "A fixed message: a person will reply. No wrong day reaches the citizen." },
      ]}
    />
  );
}

function LgAgenticRag() {
  return (
    <SketchSteps
      title="Search, grade, rewrite once"
      intro="Press Play to follow the bottled-water question."
      label="Agentic RAG"
      steps={[
        { label: "search_or_answer", says: "The model decides the question needs the rulebook and searches 'refund bottled water'." },
        { label: "retrieve", says: "The two closest sections come back: both about tankers." },
        { label: "grade", says: "Do they answer the question? No, and no rewrite was tried yet: rewrite_question." },
        { label: "rewrite", says: "The model rewrites the question in rulebook words; rewrites becomes 1." },
        { label: "search again", says: "A second search finds reconnection and meter rules: still no answer." },
        { label: "answer", says: "One rewrite was used, so answer runs: the rulebook does not cover it, a person will be asked." },
      ]}
    />
  );
}

function LgSubgraph() {
  return (
    <SketchSteps
      title="Two offices, two ways to connect"
      intro="Press Play to follow two tickets."
      label="Subgraphs"
      steps={[
        { label: "triage", says: "T-4490 is a billing complaint: go to the billing node." },
        { label: "billing", says: "The billing graph itself is the node. It reads phone from the desk's state." },
        { label: "inside billing", says: "load_readings, then check_jump: four times the average, so the bill is held." },
        { label: "merge back", says: "The shared key verdict comes back to the desk; readings stays inside." },
        { label: "repairs", says: "T-4492 is a leak. The repairs function sends {'job': 'T-4492'} to the repair graph." },
        { label: "translate back", says: "The job's log comes back as the ticket's repair_log." },
      ]}
    />
  );
}

function LgSupervisor() {
  return (
    <SketchSteps
      title="A supervisor and two specialists"
      intro="Press Play to follow a message with two problems."
      label="Multi-agent"
      steps={[
        { label: "supervisor", says: "Reads the message: a high bill and a dripping meter. Command(goto='billing')." },
        { label: "billing", says: "Its own agent checks bills and readings, holds the bill, and reports back, signed 'billing'." },
        { label: "supervisor", says: "Reads the report: the meter is still open. Command(goto='repairs')." },
        { label: "repairs", says: "Books a visit for the meter, and, having read everything, one for the inspection too." },
        { label: "supervisor", says: "Every problem has a report: FINISH, and the run ends." },
      ]}
    />
  );
}

function LgStream() {
  return (
    <SketchSteps
      title="What reaches the screen, and when"
      intro="Press Play to follow one update request."
      label="Streaming"
      steps={[
        { label: "0.00 s", says: "lookup starts and writes 'finding your tickets': a custom event, shown at once." },
        { label: "0.50 s", says: "The tickets are found: 'found 2, checking the crew schedule'." },
        { label: "1.0 s", says: "lookup ends; the reply node calls the model." },
        { label: "2.22 s", says: "The first token arrives as a messages chunk from the reply node." },
        { label: "3.73 s", says: "The last of 72 chunks. Without streaming, the screen would have been empty until now." },
      ]}
    />
  );
}

function LgFunctional() {
  return (
    <SketchSteps
      title="A crash and a resume, in a function"
      intro="Press Play to follow job J-301."
      label="Functional API"
      steps={[
        { label: "start", says: "repair_job runs. book_crew(job).result(): the crew is booked, and the result saved." },
        { label: "order_parts", says: "Ordered, and the result saved." },
        { label: "send_sms", says: "The SMS gateway times out: the entrypoint fails; the two results stay in the checkpoint." },
        { label: "resume", says: "invoke(None, config) runs repair_job again from its first line." },
        { label: "replay", says: "book_crew and order_parts return their saved results at once: nothing is booked twice." },
        { label: "send_sms", says: "This one runs for real, succeeds, and the function returns the three log lines." },
      ]}
    />
  );
}

function LgMutation() {
  return (
    <SketchSteps
      title="How the checks judge your tests"
      intro="Press Play to follow one test through the check."
      label="Planted bugs"
      steps={[
        { label: "Correct desk", says: "Your test runs against the reference desk.py. It must pass." },
        { label: "Plant a bug", says: "The check changes one line: TEAMS forgets dirty water." },
        { label: "Run again", says: "Your test runs against the broken desk." },
        { label: "Fails?", says: "A good test fails here: it noticed the bug. The task passes." },
        { label: "Passes?", says: "A test that still passes would not notice this mistake: the check says it is too weak." },
      ]}
    />
  );
}

function LgServer() {
  return (
    <SketchSteps
      title="One message through the server"
      intro="Press Play to follow 'Any update?' from client.py."
      label="Server"
      steps={[
        { label: "threads.create", says: "The client asks for a thread; the server returns its id." },
        { label: "runs.wait", says: "The client sends the message as JSON on that thread, for the graph named harsh." },
        { label: "load", says: "The server loads the thread's saved state: empty the first time." },
        { label: "run", says: "It runs harsh/graph.py's graph: agent, tools, agent." },
        { label: "save", says: "It saves the thread itself; the graph has no checkpointer of its own." },
        { label: "answer", says: "runs.wait returns the final state; the client prints the last message." },
      ]}
    />
  );
}

function LgDeepAgent() {
  return (
    <SketchSteps
      title="The planner, its files and its helper"
      intro="Press Play to follow the monsoon plan."
      label="Deep agent"
      steps={[
        { label: "read_file", says: "The planner reads /pipes.csv and /crews.md: small files, real data/ on disk." },
        { label: "permission", says: "It may not read /complaints_2025.csv: 149 rows stay out of its context." },
        { label: "task", says: "It hands the counting to the data-analyst, with a description of what it needs." },
        { label: "count_complaints", says: "The analyst counts with Python, in its own fresh context, and returns one answer." },
        { label: "write_file", says: "The planner writes /plan.md, which is data/plan.md on disk." },
        { label: "check", says: "Counts from Python are exact; the ages and crew days it worked out itself are not." },
      ]}
    />
  );
}

function LgResearch() {
  return (
    <SketchSteps
      title="A research team"
      intro="Press Play to follow the Station Road study."
      label="Research"
      steps={[
        { label: "plan", says: "The planner sees the seven records and writes seven questions." },
        { label: "Send", says: "Seven researchers start at once, each with one question." },
        { label: "research", says: "Each reads the sources it needs and returns a Finding with its sources." },
        { label: "reducer", says: "operator.add collects the seven findings into one list." },
        { label: "write", says: "The writer turns the findings into paragraphs, each ending with its sources." },
        { label: "review", says: "Python checks every paragraph's citations; problems go back to the writer once." },
      ]}
    />
  );
}

function LgCapstone() {
  return (
    <SketchSteps
      title="Harsh, complete"
      intro="Press Play to follow a burst main."
      label="Capstone"
      steps={[
        { label: "intake", says: "The model reads the message: kind repair, problem main_burst, street Station Road." },
        { label: "route_intent", says: "kind repair: go to the repair node." },
        { label: "repair", says: "REPAIR_COST says Rs 65,000: over 50,000, so interrupt and wait." },
        { label: "server", says: "The run is saved; the client shows that the engineer is being asked." },
        { label: "engineer", says: "Her app sends command={'resume': {'approve': True}} on the same thread." },
        { label: "booked", says: "repair runs again, gets the approval, and books a crew. For Thursday: the urgency was never checked." },
      ]}
    />
  );
}

function RsCargoRun() {
  return (
    <SketchSteps
      title="What cargo run does"
      intro="Press Play to follow hello_windwatch.rs to the screen."
      label="cargo run"
      steps={[
        { label: "cargo run", says: "Cargo reads Cargo.toml to find the crate and the program you asked for." },
        { label: "changed?", says: "It compares the files with the last build; if nothing changed, it skips straight to running." },
        { label: "rustc", says: "The compiler checks every rule (types, ownership) and refuses the build if one is broken." },
        { label: "machine code", says: "It writes a real program for this processor into the build folder." },
        { label: "run", says: "Cargo starts that program; it prints its two lines. No compiler or interpreter is involved any more." },
      ]}
    />
  );
}

function RsShadowing() {
  return (
    <SketchSteps
      title="One name, four values"
      intro='Press Play to follow "  12.5 m/s" into a number.'
      label="Shadowing"
      steps={[
        { label: "let speed = text.trim()", says: 'speed is "12.5 m/s": text, without the outer spaces.' },
        { label: 'let speed = ...trim_end_matches("m/s").trim()', says: 'A new speed: "12.5". The old one can no longer be reached.' },
        { label: "let speed: f64 = speed.parse().unwrap()", says: "A new speed of another type: the number 12.5." },
        { label: "speed", says: "The last line returns the number. Nothing was changed in place, so no mut was needed." },
      ]}
    />
  );
}

function RsOverflow() {
  return (
    <SketchSteps
      title="250 + 10 in eight bits"
      intro="Press Play to add 10 faults to a u8 holding 250."
      label="Overflow"
      steps={[
        { label: "250", says: "In binary, 250 is 11111010: all eight bits of a u8 are nearly full." },
        { label: "+ 10", says: "The sum is 260, which needs nine bits: 1 00000100." },
        { label: "debug build", says: "Rust checks every sum and stops: attempt to add with overflow, with the file and line." },
        { label: "release build", says: "No check: only the low eight bits stay, 00000100, which is 4." },
        { label: "the fix", says: "checked_add returns None when it does not fit, so the code decides what happens." },
      ]}
    />
  );
}

function RsExpression() {
  return (
    <SketchSteps
      title="The last line of a function"
      intro="Press Play to compare the two versions of tip_speed."
      label="Expressions"
      steps={[
        { label: "no semicolon", says: "2.0 * PI * blade_m * rotor_rpm / 60.0 is an expression: its value, an f64, is the function's value." },
        { label: "returned", says: "The caller gets 62.83 for 12 rpm and 50 m blades." },
        { label: "with a semicolon", says: "The same line ends with ; and becomes a statement: it computes the number and throws it away." },
        { label: "()", says: "The function body now gives (), the unit value, but it promised an f64." },
        { label: "refused", says: "The compiler stops: expected f64, found (), and points at the semicolon to remove." },
      ]}
    />
  );
}

function RsDayLoop() {
  return (
    <SketchSteps
      title="A day of wind, hour by hour"
      intro="Press Play to count Monday's generating hours."
      label="for loop"
      steps={[
        { label: "hours = 0", says: "let mut hours = 0: a counter that is allowed to change." },
        { label: "00:00 to 03:00", says: "2.1, 1.8, 1.5, 2.4 m/s: too calm. The counter stays at 0." },
        { label: "04:00 to 17:00", says: "3.1 to 23.5 m/s: generating, 14 times. The counter reaches 14." },
        { label: "18:00 and 19:00", says: "26.1 and 28.4 m/s: storm stop. The counter stays at 14." },
        { label: "20:00 to 23:00", says: "22.0 down to 6.2 m/s: generating again, 4 more hours." },
        { label: "return", says: "The loop ends after 24 values; hours, 18, is returned." },
      ]}
    />
  );
}

function RsMove() {
  return (
    <SketchSteps
      title="What let backup = log does"
      intro="Press Play to follow a vector through a move."
      label="Move"
      steps={[
        { label: "vec![2100.0, 2250.0]", says: "log's small part on the stack (pointer, length, capacity) points at two numbers on the heap." },
        { label: "let backup = log", says: "The stack part is copied into backup. The heap numbers are not copied." },
        { label: "log is moved", says: "The compiler marks log as moved: using it again is an error, so only one owner points at the heap." },
        { label: "end of the block", says: "backup goes out of scope and frees the heap block, once. log frees nothing: it owns nothing." },
        { label: "clone()", says: "log.clone() instead makes a second heap block: two owners, two blocks, each freed once." },
      ]}
    />
  );
}

function RsBorrow() {
  return (
    <SketchSteps
      title="Many readers, or one writer"
      intro="Press Play to see why push is refused."
      label="Borrowing"
      steps={[
        { label: "let first = &log[0]", says: "A shared reference points at the first number in log's heap block." },
        { label: "log.push(1980.0)", says: "push needs a mutable borrow, and may move the whole block to a bigger place in memory." },
        { label: "the danger", says: "If it moved, first would point at memory already given back: a crash in C." },
        { label: "first is used later", says: "Because first is still used after push, the two borrows overlap." },
        { label: "refused", says: "E0502: cannot borrow log as mutable because it is also borrowed as immutable. Nothing is built." },
        { label: "the fix", says: "Use first before pushing, or copy the number out: let first = log[0];" },
      ]}
    />
  );
}

function RsSlice() {
  return (
    <SketchSteps
      title="A slice of a log line"
      intro="Press Play to take the turbine id out of a line."
      label="Slices"
      steps={[
        { label: "the line", says: '"T07,2026-11-24 10:10,12.4,2100" is 30 bytes owned by the caller.' },
        { label: "find(',')", says: "The first comma is at byte 3." },
        { label: "&line[..3]", says: "A slice: a pointer to byte 0 of the same text, and a length of 3. Nothing is copied." },
        { label: '"T07"', says: "The slice reads as T07. It may not outlive the line it points into." },
        { label: "past the end", says: "&line[..40] would panic: a slice always checks its range against the real length." },
      ]}
    />
  );
}

function RsOption() {
  return (
    <SketchSteps
      title="A peak that may not exist"
      intro="Press Play to follow two logs into peak_power."
      label="Option"
      steps={[
        { label: "Monday", says: "Three readings: peak_power returns Some(2400.0), the number wrapped in Some." },
        { label: "Tuesday", says: "No readings: there is no peak, so peak_power returns None. No made-up zero, no null." },
        { label: "the caller", says: "An Option<f64> is not an f64: adding 100 to it does not compile." },
        { label: "deciding", says: "The caller opens it: match, if let, or unwrap_or(0.0), where everyone can see the choice." },
        { label: "printed", says: "Monday shows 2400, Tuesday shows 0, because the caller chose 0 for None." },
      ]}
    />
  );
}

function RsLetElse() {
  return (
    <SketchSteps
      title="Three gates for a log line"
      intro="Press Play to send three lines through parse_line."
      label="let else"
      steps={[
        { label: "gate 1: four fields", says: "let [turbine, time, wind, power] = parts[..] else { return None };" },
        { label: "12.9 with three fields", says: '"T07,...,12.9" has three parts: it does not fit, so None.' },
        { label: "gate 2: wind is a number", says: '"windy" cannot be parsed into an f64: None.' },
        { label: "gate 3: power is a number", says: '"22O0" has a letter O: None.' },
        { label: "through", says: '"T07,...,12.4,2100" passes all three gates and becomes Some(Reading { ... }).' },
      ]}
    />
  );
}

function RsModules() {
  return (
    <SketchSteps
      title="Borders inside a crate"
      intro="Press Play to follow a call from main.rs to reading.rs."
      label="Modules"
      steps={[
        { label: "lib.rs", says: "The crate root says pub mod reading; pub mod report;, so the two files are part of the crate." },
        { label: "main.rs", says: "Outside the library: it may only use pub items, by paths starting with ch12_modules." },
        { label: "summary_text", says: "lib.rs calls report::farm_summary: it must be pub, even for the parent module." },
        { label: "farm_summary", says: "report.rs uses crate::reading::parse_line, a pub function in a sibling module." },
        { label: "pub use", says: "lib.rs re-exports farm_summary, so outsiders can write ch12_modules::farm_summary." },
      ]}
    />
  );
}

function RsWindows() {
  return (
    <SketchSteps
      title="A moving average of three"
      intro="Press Play to slide the window along T07's log."
      label="windows(3)"
      steps={[
        { label: "10:10 to 10:30", says: "2100, 2180, 2490: the first window. Average 2256.7." },
        { label: "10:20 to 10:40", says: "The window moves one reading: 2180, 2490, 1650. Average 2106.7." },
        { label: "10:30 to 10:50", says: "2490, 1650, 2210: the gust and the drop in one window. Average 2116.7." },
        { label: "10:40 to 11:00", says: "1650, 2210, 2240. Average 2033.3. There is no fifth window: it would run past the end." },
        { label: "result", says: "Six readings, four averages, swinging 223 kW instead of 840." },
      ]}
    />
  );
}

function RsEntry() {
  return (
    <SketchSteps
      title="Totals per turbine with entry()"
      intro="Press Play to add three log lines into the map."
      label="HashMap entry"
      steps={[
        { label: "T07, 2100 kW", says: 'entry("T07") finds no slot: or_insert(0.0) makes one at 0.0, then += 350.0.' },
        { label: "T12, 140 kW", says: "A new key again: T12 starts at 0.0, then += 23.3." },
        { label: "T07, 2180 kW", says: 'entry("T07") finds the slot by its hash at once: 350.0 += 363.3 makes 713.3.' },
        { label: 'get("T40")', says: "No slot for T40: None, not a crash and not a zero." },
        { label: "order", says: "Iterating the map gives the keys in an order that depends on the hash: it changes from run to run." },
      ]}
    />
  );
}

function RsQuestionMark() {
  return (
    <SketchSteps
      title="Two ? exits in parse_reading"
      intro="Press Play to follow a broken line through the function."
      label="? operator"
      steps={[
        { label: "four fields", says: '"T07,10:50,13.4,22O0" has four fields: the length check passes.' },
        { label: 'number("13.4")?', says: "Ok(13.4): ? takes the 13.4 out, and the function goes on." },
        { label: 'number("22O0")?', says: 'Err("power is not a number: ..."): ? returns this Err from parse_reading at once.' },
        { label: "never reached", says: "The Ok(Reading { ... }) line does not run for this line." },
        { label: "the caller", says: 'main gets the Err and prints it: line 5: power is not a number: "22O0".' },
      ]}
    />
  );
}

function RsErrorChain() {
  return (
    <SketchSteps
      title="How the error message is built"
      intro="Press Play to follow line 3 of t12.log up to main."
      label="Error chain"
      steps={[
        { label: "parse_reading", says: "9999 kW is more than 2500: Err(ReadingError::TooMuchPower { kw: 9999.0 })." },
        { label: "with_context", says: 'load wraps it: "data/t12.log, line 3", with the TooMuchPower error kept as its cause.' },
        { label: "?", says: "load returns the wrapped error to main, converted into an anyhow::Error." },
        { label: "main returns Err", says: 'Rust prints "Error:" and the context, then "Caused by:" and the original message.' },
        { label: "exit code", says: "The program exits with 1, so a script or a scheduler can see it failed." },
      ]}
    />
  );
}

const DIAGRAMS: Record<string, () => JSX.Element> = {
  "rs-windows": RsWindows,
  "rs-entry": RsEntry,
  "rs-question-mark": RsQuestionMark,
  "rs-error-chain": RsErrorChain,
  "rs-option": RsOption,
  "rs-let-else": RsLetElse,
  "rs-modules": RsModules,
  "rs-move": RsMove,
  "rs-borrow": RsBorrow,
  "rs-slice": RsSlice,
  "rs-cargo-run": RsCargoRun,
  "rs-shadowing": RsShadowing,
  "rs-overflow": RsOverflow,
  "rs-expression": RsExpression,
  "rs-day-loop": RsDayLoop,
  "lg-mutation": LgMutation,
  "lg-server": LgServer,
  "lg-deep-agent": LgDeepAgent,
  "lg-research": LgResearch,
  "lg-capstone": LgCapstone,
  "lg-agent-loop": LgAgentLoop,
  "lg-reflection": LgReflection,
  "lg-agentic-rag": LgAgenticRag,
  "lg-subgraph": LgSubgraph,
  "lg-supervisor": LgSupervisor,
  "lg-stream": LgStream,
  "lg-functional": LgFunctional,
  "lg-threads": LgThreads,
  "lg-summary": LgSummary,
  "lg-durable": LgDurable,
  "lg-interrupt": LgInterrupt,
  "lg-fork": LgFork,
  "lg-store": LgStore,
  "lg-run": LgRun,
  "lg-reducer": LgReducer,
  "lg-route": LgRoute,
  "lg-model-node": LgModelNode,
  "lg-join": LgJoin,
  "lg-send": LgSend,
  "lc-middleware": LcMiddleware,
  "lc-human-loop": LcHumanLoop,
  "lc-rag": LcRag,
  "lc-mcp": LcMcp,
  "lc-agent-loop": LcAgentLoop,
  "lc-memory-threads": LcMemoryThreads,
  "lc-ai-circles": LcAiCircles,
  "lc-next-token": LcNextToken,
  "lc-chat-request": LcChatRequest,
  "l4j-streaming": L4jStreaming,
  "l4j-memory-window": L4jMemoryWindow,
  "l4j-mcp": L4jMcp,
  "l4j-vector-search": L4jVectorSearch,
  "l4j-guardrails": L4jGuardrails,
  "l4j-supervisor": L4jSupervisor,
  "l4j-sequence": L4jSequence,
  "l4j-workflow": L4jWorkflow,
  "l4j-tool-call": L4jToolCall,
  "l4j-rag": L4jRag,
  "l4j-ai-service": L4jAiService,
  "l4j-http-call": L4jHttpCall,
  "l4j-ai-circles": L4jAiCircles,
  "l4j-neuron": L4jNeuron,
  "l4j-context-window": L4jContextWindow,
  "l4j-embedding-space": L4jEmbeddingSpace,
  "l4j-attention": L4jAttention,
  "l4j-llm-pipeline": L4jLlmPipeline,
  "ai-vision": AiVision,
  "ai-evaluation": AiEvaluation,
  "ai-guardrails": AiGuardrails,
  "ai-cost-meter": AiCostMeter,
  "ai-workflows": AiWorkflows,
  "ai-atlas-live": AiAtlasLive,
  "ai-embeddings": AiEmbeddings,
  "ai-vector-store": AiVectorStore,
  "ai-etl": AiEtl,
  "ai-rag": AiRag,
  "ai-memory": AiMemory,
  "ai-tool-calling": AiToolCalling,
  "ai-tool-confirmation": AiToolConfirmation,
  "ai-tool-context": AiToolContext,
  "ai-advisor-chain": AiAdvisorChain,
  "ai-mcp": AiMcp,
  "ai-request-flow": AiRequestFlow,
  "ai-roles": AiRoles,
  "ai-temperature": AiTemperature,
  "ai-streaming": AiStreaming,
  "ai-structured": AiStructured,
  "linux-tree": LinuxTree,
  "linux-glob": LinuxGlob,
  "linux-streams": LinuxStreams,
  "linux-pipe": LinuxPipe,
  "linux-permissions": LinuxPermissions,
  "linux-signals": LinuxSignals,
  "linux-open-file": LinuxOpenFile,
  "linux-for-loop": LinuxForLoop,
  "linux-env": LinuxEnv,
  "linux-ports": LinuxPorts,
  "linux-cron": LinuxCron,
  "git-three-areas": GitThreeAreas,
  "git-branch-pointer": GitBranchPointer,
  "git-merge": GitMerge,
  "git-conflict": GitConflict,
  "git-undo-map": GitUndoMap,
  "git-reflog": GitReflog,
  "git-stash": GitStash,
  "git-push-pull": GitPushPull,
  "git-pull-request": GitPullRequest,
  "git-rebase": GitRebase,
  "git-objects": GitObjects,
  "left-join": LeftJoin,
  "latency-ladder": LatencyLadder,
  "hit-rate-savings": HitRateSavings,
  "one-at-a-time": OneAtATime,
  "cache-aside-flow": CacheAsideFlow,
  stampede: Stampede,
  "lock-flow": LockFlow,
  "slow-command": SlowCommand,
  "eviction-lru": EvictionLru,
  "go-channels": GoChannels,
  "go-panic-trace": GoPanicTrace,
  "go-runs-a-file": GoRunsAFile,
  "js-event-loop": JsEventLoop,
  "js-stack-trace": JsStackTrace,
  "node-runs-a-file": NodeRunsAFile,
  "java-try-catch": JavaTryCatch,
  "java-object-creation": JavaObjectCreation,
  "java-stack-trace": JavaStackTrace,
  "java-method-call": JavaMethodCall,
  "java-runs-a-file": JavaRunsAFile,
  "import-search": ImportSearch,
  "object-creation": ObjectCreation,
  "try-except-flow": TryExceptFlow,
  "comprehension-steps": ComprehensionSteps,
  "python-runs-a-file": PythonRunsAFile,
  "function-call": FunctionCall,
  "traceback-bottom-up": TracebackBottomUp,
  "library-vs-framework": LibraryVsFramework,
  "backend-stack": BackendStack,
  "spring-timeline": SpringTimeline,
  "startup-sequence": StartupSequence,
  "bean-lifecycle": BeanLifecycle,
  "request-journey": RequestJourney,
  "di-container": DiContainer,
  layers: Layers,
  "request-mapping": RequestMapping,
  "json-binding": JsonBinding,
  "error-flow": ErrorFlow,
  "profile-layers": ProfileLayers,
  "orm-mapping": OrmMapping,
  "one-to-many": OneToMany,
  "transaction-flow": TransactionFlow,
  "flyway-versions": FlywayVersions,
  "test-slices": TestSlices,
  "actuator-endpoints": ActuatorEndpoints,
  "security-chain": SecurityChain,
  "service-call": ServiceCall,
  "checkout-flow": CheckoutFlow,
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
