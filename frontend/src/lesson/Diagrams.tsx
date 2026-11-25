import type { ReactNode } from "react";
import { Svg } from "./PicturePrimitives";
import { SketchSteps } from "./Sketch";

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
  // Still (owner, 25 November): one real question from chapter 1's run, with the gateway's numbers.
  const rows: [string, string, BoxTone][] = [
    ["1. GET /ask?q=What is a black hole?", "a visitor's browser calls Atlas", "plain"],
    ["2. ChatClient builds the prompt", "chat.prompt().user(q): one user message", "plain"],
    ["3. Spring AI sends JSON", "{messages: [...], model: \"ai-chat\"}", "plain"],
    ["4. The LabBox gateway", "checks the budget, adds the real key, ai-chat = gpt-4o-mini", "accent"],
    ["5. The model writes", "449 tokens in 6.7 s, about 67 a second", "copy"],
    ["6. .content() returns the text", "13 in + 449 out = $0.000271", "plain"],
  ];
  return (
    <Svg viewBox="0 0 440 448" label="One question's journey: the browser calls Atlas, ChatClient builds a prompt, Spring AI sends JSON naming ai-chat, the LabBox gateway forwards it to gpt-4o-mini, the model writes 449 tokens in 6.7 seconds, and the controller returns the text">
      {rows.map(([title, detail, tone], i) => {
        const y = 4 + i * 74;
        return (
          <g key={title}>
            <Box x={28} y={y} w={406} h={56} label="" tone={tone} />
            <text className="dg-label" x={42} y={y + 22}>{title}</text>
            <text className="dg-note" x={42} y={y + 43}>{detail}</text>
            {i < rows.length - 1 && <Arrow x1={231} y1={y + 58} x2={231} y2={y + 72} />}
          </g>
        );
      })}
    </Svg>
  );
}

function AiRoles() {
  // Still (owner, 25 November): the messages of one real request from chapter 2's run.
  const rows: [string, string, string, BoxTone][] = [
    ["system", "written by you, sent with every request (79 tokens)", "You are Atlas, the friendly visitor guide of ...", "accent"],
    ["user", "written by the visitor", "Name one planet with rings.", "plain"],
    ["assistant", "written by the model, within the rules", "Saturn is a planet with beautiful rings. ...", "copy"],
  ];
  return (
    <Svg viewBox="0 0 440 300" label="One request: a system message written by the developer, a user message from the visitor, and the assistant's answer from the model">
      {rows.map(([role, who, text, tone], i) => {
        const y = 4 + i * 92;
        return (
          <g key={role}>
            <Box x={28} y={y} w={406} h={76} label="" tone={tone} />
            <text className="dg-label" x={42} y={y + 24}>{role}</text>
            <text className="dg-note" x={42} y={y + 45}>{who}</text>
            <text className="dg-note" x={42} y={y + 65}>{text}</text>
            {i < rows.length - 1 && <Arrow x1={231} y1={y + 78} x2={231} y2={y + 90} />}
          </g>
        );
      })}
      <text className="dg-note" x={28} y={292}>The next request sends the system message again.</text>
    </Svg>
  );
}

function AiTemperature() {
  // Still (owner, 25 November): real probabilities from the gateway (logprobs) and chapter 3's real runs.
  const bars: [string, number][] = [["Muse", 77], ["Art", 22.1], ["Museum", 0.3]];
  return (
    <Svg viewBox="0 0 440 352" label="The model's probabilities for the first piece of a robot name: Muse 77 percent, Art 22 percent, Museum 0.3 percent. At temperature 0 it answered MuseBot three times; at 1.5 MuseoMate, Museum Navigator and MuseoGuide">
      <text className="dg-label" x={8} y={20}>The first piece of the name, as the model rates it</text>
      {bars.map(([token, pct], i) => {
        const y = 36 + i * 40;
        return (
          <g key={token}>
            <text className="dg-note" x={8} y={y + 20}>{token}</text>
            <Box x={84} y={y} w={Math.max(4, pct * 3.1)} h={28} label="" tone={i === 0 ? "accent" : "plain"} />
            <text className="dg-note" x={92 + Math.max(4, pct * 3.1)} y={y + 20}>{pct}%</text>
          </g>
        );
      })}
      <Box x={8} y={168} w={426} h={74} label="" />
      <text className="dg-label" x={20} y={192}>temperature 0, three runs</text>
      <text className="dg-note" x={20} y={218}>MuseBot, MuseBot, MuseBot</text>
      <Box x={8} y={258} w={426} h={74} label="" tone="copy" />
      <text className="dg-label" x={20} y={282}>temperature 1.5, three runs</text>
      <text className="dg-note" x={20} y={308}>MuseoMate, Museum Navigator, MuseoGuide</text>
    </Svg>
  );
}

function AiStreaming() {
  // Still (owner, 25 November): one measured run from chapter 4 (first byte 0.96 s, all 1.94 s).
  const x0 = 96, px = 110; // 110 px a second
  const t = (sec: number) => x0 + sec * px;
  return (
    <Svg viewBox="0 0 440 250" label="The same answer two ways: with call the screen stays empty for 1.94 seconds and then the whole answer appears; with stream the first words appear at 0.96 seconds and the rest follow until 1.94 seconds">
      {[0, 1, 2, 3].map((sec) => (
        <g key={sec}>
          <line className="dg-arrow" x1={t(sec)} y1={30} x2={t(sec)} y2={186} strokeDasharray="3 4" />
          <text className="dg-note" x={t(sec) - 8} y={206}>{sec} s</text>
        </g>
      ))}
      <text className="dg-label" x={8} y={66}>call()</text>
      <Box x={t(0)} y={44} w={1.94 * px} h={34} label="screen empty" />
      <Box x={t(1.94)} y={44} w={40} h={34} label="all" tone="copy" />
      <text className="dg-label" x={8} y={136}>stream()</text>
      <Box x={t(0)} y={114} w={0.96 * px} h={34} label="empty" />
      <Box x={t(0.96)} y={114} w={0.98 * px} h={34} label="words appear" tone="copy" />
      <text className="dg-note" x={8} y={236}>Same answer, same tokens: only the empty wait is shorter.</text>
    </Svg>
  );
}

function AiStructured() {
  // Still (owner, 25 November): chapter 5's real tour request, from the gateway's log and the real answer.
  const rows: [string, string, BoxTone][] = [
    ["1. record TourPlan(title, stops)", "Spring AI writes its JSON schema", "plain"],
    ["2. the user message", "your question + \"JSON only\" + the schema", "accent"],
    ["3. the model answers, JSON only", "{\"title\":\"60 Minute Museum Tour\",\"stops\":[...]}", "plain"],
    ["4. Jackson reads it", "a TourPlan: 5 stops, 10+15+15+10+10 = 60 minutes", "copy"],
  ];
  return (
    <Svg viewBox="0 0 440 300" label="Structured output: the TourPlan record becomes a JSON schema in the user message, the model answers in JSON, and Jackson reads it into a TourPlan with five stops adding up to 60 minutes">
      {rows.map(([title, detail, tone], i) => {
        const y = 4 + i * 74;
        return (
          <g key={title}>
            <Box x={28} y={y} w={406} h={56} label="" tone={tone} />
            <text className="dg-label" x={42} y={y + 22}>{title}</text>
            <text className="dg-note" x={42} y={y + 43}>{detail}</text>
            {i < rows.length - 1 && <Arrow x1={231} y1={y + 58} x2={231} y2={y + 72} />}
          </g>
        );
      })}
    </Svg>
  );
}

function AiMemory() {
  // Still (owner, 25 November): the real tenth request of chapter 6's run (trigger 8 turns, window 4), from the gateway's log.
  const turns = [1, 2, 3, 4, 5, 6, 7, 8, 9];
  const sent: [string, string, BoxTone][] = [
    ["system", "Atlas's rules", "accent"],
    ["turns 6 to 9", "4 questions + 4 answers: Dwarf Planet ... Gas Giant.", "plain"],
    ["question 10", "Question 10: name one planet, in two words.", "copy"],
  ];
  return (
    <Svg viewBox="0 0 440 330" label="The session's log holds nine turns; after compaction only turns 6 to 9 are in the view, so the tenth request sends the system prompt, turns 6 to 9 and the new question">
      <text className="dg-label" x={8} y={18}>The session's log: 9 turns, all kept</text>
      {turns.map((n, i) => (
        <g key={n} opacity={n <= 5 ? 0.45 : 1}>
          <Box x={8 + i * 47} y={30} w={42} h={38} label={String(n)} tone={n <= 5 ? "plain" : "copy"} code />
        </g>
      ))}
      <text className="dg-note" x={8} y={88}>Turns 1 to 5 stay in the log but leave the view.</text>
      <text className="dg-label" x={8} y={124}>What the 10th request sends</text>
      {sent.map(([title, detail, tone], i) => {
        const y = 136 + i * 62;
        return (
          <g key={title}>
            <Box x={8} y={y} w={426} h={52} label="" tone={tone} />
            <text className="dg-label" x={20} y={y + 21}>{title}</text>
            <text className="dg-note" x={20} y={y + 41}>{detail.length > 58 ? detail.slice(0, 56) + "..." : detail}</text>
          </g>
        );
      })}
    </Svg>
  );
}

function AiToolCalling() {
  // Still (owner, 26 November): chapter 7's real "this Saturday" request, from the gateway's log.
  const rows: [string, string, BoxTone][] = [
    ["the visitor", "Are there free seats ... this Saturday?", "plain"],
    ["model call 1: asks for a tool", "nextDay {\"dayOfWeek\":\"SATURDAY\"}", "accent"],
    ["your Java runs it", "\"2026-11-28 (SATURDAY)\"", "copy"],
    ["model call 2: asks for a tool", "planetariumShows {\"date\":\"2026-11-28\"}", "accent"],
    ["your Java runs it", "11:00: 4 seats, 14:00: 0, 16:00: 11", "copy"],
    ["model call 3: the answer", "4 seats at 11:00, 11 at 16:00; 14:00 is fully booked", "plain"],
  ];
  return (
    <Svg viewBox="0 0 440 448" label="The real tool-calling conversation: the model asks for nextDay, Java returns 2026-11-28, the model asks for planetariumShows, Java returns the seats, and the model answers. Three model calls">
      {rows.map(([title, detail, tone], i) => {
        const y = 4 + i * 74;
        return (
          <g key={i}>
            <Box x={28} y={y} w={406} h={56} label="" tone={tone} />
            <text className="dg-label" x={42} y={y + 22}>{title}</text>
            <text className="dg-note" x={42} y={y + 43}>{detail}</text>
            {i < rows.length - 1 && <Arrow x1={231} y1={y + 58} x2={231} y2={y + 72} />}
          </g>
        );
      })}
    </Svg>
  );
}

function AiToolConfirmation() {
  // Still (owner, 26 November): chapter 8's real booking, paused and confirmed.
  const rows: [string, string, BoxTone][] = [
    ["the visitor (ria)", "Please book 2 seats for ... 16:00 on 2026-11-28.", "plain"],
    ["model call 1: proposes", "bookSeats {date: 2026-11-28, time: 16:00, seats: 2}", "accent"],
    ["Spring AI pauses: nothing booked", "/book returns a pendingId and the pending call", "highlight"],
    ["the visitor decides", "yes: allow(key); no: deny(key, message)", "plain"],
    ["Java runs bookSeats (only on yes)", "Booked 2 seats for ria at the 16:00 show ...", "copy"],
    ["model call 2: the answer", "I have booked 2 seats for you ... Enjoy the show!", "plain"],
  ];
  return (
    <Svg viewBox="0 0 440 448" label="The model proposes bookSeats, Spring AI pauses and returns the pending call, the visitor says yes or no, the tool runs only on yes, and the model answers">
      {rows.map(([title, detail, tone], i) => {
        const y = 4 + i * 74;
        return (
          <g key={i}>
            <Box x={28} y={y} w={406} h={56} label="" tone={tone} />
            <text className="dg-label" x={42} y={y + 22}>{title}</text>
            <text className="dg-note" x={42} y={y + 43}>{detail}</text>
            {i < rows.length - 1 && <Arrow x1={231} y1={y + 58} x2={231} y2={y + 72} />}
          </g>
        );
      })}
    </Svg>
  );
}

function AiToolContext() {
  // Still (owner, 26 November): chapter 8's real "for my friend Sam" booking, from the gateway's log.
  return (
    <Svg viewBox="0 0 440 330" label="The model fills date, time and seats; the app puts visitor ria in the tool context, around the model; bookSeats books for ria, although the visitor asked for Sam">
      <Box x={8} y={4} w={204} h={96} label="" />
      <text className="dg-label" x={20} y={28}>the model's arguments</text>
      <text className="dg-note" x={20} y={52}>date: 2026-11-28</text>
      <text className="dg-note" x={20} y={72}>time: 16:00</text>
      <text className="dg-note" x={20} y={92}>seats: 1</text>
      <Box x={228} y={4} w={206} h={96} label="" tone="accent" />
      <text className="dg-label" x={240} y={28}>the app's tool context</text>
      <text className="dg-note" x={240} y={52}>visitor: ria</text>
      <text className="dg-note" x={240} y={72}>(the model never sees it)</text>
      <Arrow x1={110} y1={102} x2={180} y2={138} />
      <Arrow x1={330} y1={102} x2={262} y2={138} />
      <Box x={120} y={140} w={200} h={40} label="bookSeats" tone="copy" code />
      <Arrow x1={220} y1={182} x2={220} y2={204} />
      <Box x={8} y={206} w={426} h={56} label="" tone="copy" />
      <text className="dg-label" x={20} y={228}>the tool's result</text>
      <text className="dg-note" x={20} y={250}>Booked 1 seats for ria at the 16:00 show on 2026-11-28.</text>
      <text className="dg-note" x={8} y={290}>The visitor asked "for my friend Sam": the booking is Ria's.</text>
      <text className="dg-note" x={8} y={310}>(The model's sentence still said "for your friend Sam".)</text>
    </Svg>
  );
}

function AiAdvisorChain() {
  // Still (owner, 26 November): chapter 9's real Marathi call (154 tokens), the advisors as nested boxes.
  return (
    <Svg viewBox="0 0 440 330" label="UsageAdvisor wraps LanguageAdvisor, which wraps the model call: on the way in LanguageAdvisor adds Answer in Marathi to the system message; on the way back UsageAdvisor counts 154 tokens">
      <g className="dg-box dg-plain"><rect x={8} y={8} width={424} height={290} rx={12} /></g>
      <text className="dg-label" x={22} y={32}>UsageAdvisor</text>
      <text className="dg-note" x={22} y={52}>on the way back: calls + 1, tokens + 154</text>
      <g className="dg-box dg-accent"><rect x={34} y={66} width={372} height={176} rx={10} /></g>
      <text className="dg-label" x={48} y={90}>LanguageAdvisor</text>
      <text className="dg-note" x={48} y={110}>on the way in: adds "Answer in Marathi."</text>
      <text className="dg-note" x={48} y={128}>to the end of the system message</text>
      <Box x={120} y={150} w={200} h={64} label="the model: 104 in, 50 out" tone="copy" />
      <text className="dg-note" x={22} y={272}>chain.nextCall(request) passes the request inward;</text>
      <text className="dg-note" x={22} y={290}>the response comes back out through the same boxes.</text>
      <text className="dg-note" x={8} y={322}>Here both have order 0: give them different orders when it matters.</text>
    </Svg>
  );
}

function AiMcp() {
  // Still (owner, 26 November): chapter 10's real MCP session with curl, four messages and their answers.
  const rows: [string[], string[]][] = [
    [["initialize"], ["atlas-museum 1.0.0,", "and an Mcp-Session-Id"]],
    [["notifications/", "initialized"], ["202, no body"]],
    [["tools/list"], ["today, openingHours,", "planetariumShows, nextDay"]],
    [["tools/call", "planetariumShows 2026-11-28"], ["11:00: 4 seats, 14:00: 0,", "16:00: 11"]],
  ];
  return (
    <Svg viewBox="0 0 440 356" label="An MCP client sends initialize, notifications/initialized, tools/list and tools/call to Atlas at /mcp; the server answers with its name and a session id, 202, four tools, and Saturday's seats">
      <text className="dg-label" x={8} y={18}>the client sends (POST /mcp)</text>
      <text className="dg-label" x={232} y={18}>Atlas answers</text>
      {rows.map(([msg, answer], i) => {
        const y = 30 + i * 80;
        return (
          <g key={i}>
            <Box x={8} y={y} w={204} h={60} label="" tone="accent" />
            {msg.map((line, j) => <text key={j} className="dg-note" x={18} y={y + (msg.length === 1 ? 35 : 26 + j * 20)}>{line}</text>)}
            <Arrow x1={213} y1={y + 30} x2={226} y2={y + 30} />
            <Box x={228} y={y} w={206} h={60} label="" tone="copy" />
            {answer.map((line, j) => <text key={j} className="dg-note" x={238} y={y + (answer.length === 1 ? 35 : 26 + j * 20)}>{line}</text>)}
          </g>
        );
      })}
    </Svg>
  );
}

function AiEmbeddings() {
  // Still (owner, 26 November): real cosine scores from text-embedding-3-small, computed for chapter 11's exhibits.
  const bars: [string, number][] = [
    ["Foucault pendulum", 0.468], ["Planetarium dome", 0.374], ["Whispering dishes", 0.257],
    ["Prism room", 0.205], ["Bicycle generator", 0.158], ["Rajasaurus", 0.087],
  ];
  return (
    <Svg viewBox="0 0 440 300" label="Cosine similarity of the question Which exhibit shows that the Earth spins with each exhibit: Foucault pendulum 0.468, Planetarium dome 0.374, Whispering dishes 0.257, Prism room 0.205, Bicycle generator 0.158, Rajasaurus 0.087">
      <text className="dg-label" x={8} y={18}>"Which exhibit shows that the Earth spins?"</text>
      {bars.map(([name, score], i) => {
        const y = 34 + i * 40;
        const w = score * 460;
        return (
          <g key={name}>
            <text className="dg-note" x={8} y={y + 20}>{name}</text>
            <Box x={150} y={y} w={w} h={28} label="" tone={i === 0 ? "copy" : "plain"} />
            <text className="dg-note" x={158 + w} y={y + 20}>{score.toFixed(3)}</text>
          </g>
        );
      })}
      <text className="dg-note" x={8} y={292}>The pendulum never says "spins", yet it ranks first.</text>
    </Svg>
  );
}

function AiVectorStore() {
  // Still (owner, 26 November): chapter 12's real start-up and one real search, from the backend's log and the app.
  const rows: [string, string, BoxTone][] = [
    ["at start-up: 12 exhibit cards", "each a Document: text + metadata (file)", "plain"],
    ["store.add(documents)", "12 embedding requests, about 0.4 s apart", "accent"],
    ["the vector store", "12 x (text, 1,536 numbers, file)", "copy"],
    ["a search: \"Where is the pendulum?\"", "1 embedding request, for the question only", "plain"],
    ["topK 3, similarityThreshold 0.5", "foucault-pendulum.md 0.637; the next was 0.292", "copy"],
  ];
  return (
    <Svg viewBox="0 0 440 374" label="At start-up twelve cards are embedded once, in twelve requests, and stored with their metadata; a search embeds only the question and returns the pendulum card with 0.637">
      {rows.map(([title, detail, tone], i) => {
        const y = 4 + i * 74;
        return (
          <g key={i}>
            <Box x={28} y={y} w={406} h={56} label="" tone={tone} />
            <text className="dg-label" x={42} y={y + 22}>{title}</text>
            <text className="dg-note" x={42} y={y + 43}>{detail}</text>
            {i < rows.length - 1 && <Arrow x1={231} y1={y + 58} x2={231} y2={y + 72} />}
          </g>
        );
      })}
    </Svg>
  );
}

function AiEtl() {
  // Still (owner, 26 November): chapter 13's real pipeline counts and one real search.
  const rows: [string, string, BoxTone][] = [
    ["extract: 12 Markdown cards", "MarkdownDocumentReader, file in the metadata", "plain"],
    ["14 documents", "a new one at each heading (the visitor card has 3)", "accent"],
    ["transform: TokenTextSplitter(100)", "23 chunks, each keeps its file", "accent"],
    ["load: vectorStore.add(chunks)", "23 embeddings in the store", "copy"],
    ["\"How much is a ticket for a child?\"", "visitor-information.md 0.407 (the whole card: 0.219)", "copy"],
  ];
  return (
    <Svg viewBox="0 0 440 374" label="Twelve cards are read into fourteen documents, split into twenty-three chunks of up to one hundred tokens, and loaded; the ticket question now finds the ticket chunk with 0.407">
      {rows.map(([title, detail, tone], i) => {
        const y = 4 + i * 74;
        return (
          <g key={i}>
            <Box x={28} y={y} w={406} h={56} label="" tone={tone} />
            <text className="dg-label" x={42} y={y + 22}>{title}</text>
            <text className="dg-note" x={42} y={y + 43}>{detail}</text>
            {i < rows.length - 1 && <Arrow x1={231} y1={y + 58} x2={231} y2={y + 72} />}
          </g>
        );
      })}
    </Svg>
  );
}

function AiRag() {
  // Still (owner, 26 November): chapter 14's real ticket question, from the gateway's log.
  const rows: [string, string, BoxTone][] = [
    ["the visitor", "How much is a ticket for a child?", "plain"],
    ["retrieve: topK 3, threshold 0.35", "1 chunk passed: visitor-information.md (0.407)", "accent"],
    ["augment: the user message becomes", "question + the chunk between dashes + the rules", "accent"],
    ["generate: the model reads it", "A ticket for a child aged 5 to 15 costs 60 rupees.", "copy"],
  ];
  return (
    <Svg viewBox="0 0 440 300" label="Retrieve, augment, generate: the ticket question finds one chunk above the threshold, the chunk is added to the user message with instructions, and the model answers 60 rupees">
      {rows.map(([title, detail, tone], i) => {
        const y = 4 + i * 74;
        return (
          <g key={i}>
            <Box x={28} y={y} w={406} h={56} label="" tone={tone} />
            <text className="dg-label" x={42} y={y + 22}>{title}</text>
            <text className="dg-note" x={42} y={y + 43}>{detail}</text>
            {i < rows.length - 1 && <Arrow x1={231} y1={y + 58} x2={231} y2={y + 72} />}
          </g>
        );
      })}
    </Svg>
  );
}

function AiVision() {
  // Still (owner, 26 November): chapter 15's real pendulum photo, with the gateway's token counts.
  const rows: [string, string, BoxTone][] = [
    ["the visitor's photo", "800 x 600 pixels: 4 tiles, 25,596 tokens", "plain"],
    ["Photos.shrink(bytes, 512)", "512 x 384 pixels, JPEG: 1 tile", "accent"],
    ["one user message, two parts", "text: What is this exhibit?  +  the image as a data URL", "accent"],
    ["the model reads both", "8,595 tokens in: 2,833 + 5,667 for the tile + the question", "copy"],
    ["the answer, in words", "This exhibit is likely a Foucault pendulum.", "plain"],
  ];
  return (
    <Svg viewBox="0 0 440 374" label="The photo is shrunk from 800 by 600 to 512 pixels, one tile instead of four, sent with the question in one message, and costs 8,595 tokens instead of 25,596">
      {rows.map(([title, detail, tone], i) => {
        const y = 4 + i * 74;
        return (
          <g key={i}>
            <Box x={28} y={y} w={406} h={56} label="" tone={tone} />
            <text className="dg-label" x={42} y={y + 22}>{title}</text>
            <text className="dg-note" x={42} y={y + 43}>{detail}</text>
            {i < rows.length - 1 && <Arrow x1={231} y1={y + 58} x2={231} y2={y + 72} />}
          </g>
        );
      })}
    </Svg>
  );
}

function AiEvaluation() {
  // Still (owner, 26 November): chapter 16's two measurements, with the real numbers.
  return (
    <Svg viewBox="0 0 440 330" label="Retrieval: 15 golden questions searched, 10 hits and 5 misses, the same every run. Answers: a judge model says YES or NO for each answer; the ticket answer passed, the broad question failed, and the T-rex answer passed once and failed once">
      <Box x={8} y={4} w={204} h={300} label="" tone="accent" />
      <text className="dg-label" x={20} y={28}>retrieval</text>
      <text className="dg-note" x={20} y={56}>15 golden questions</text>
      <text className="dg-note" x={20} y={78}>search: top 3, at least 0.35</text>
      <text className="dg-note" x={20} y={100}>is the golden card found?</text>
      <Box x={20} y={118} w={180} h={44} label="10 hits, 5 misses" tone="copy" />
      <text className="dg-note" x={20} y={190}>the same on every run:</text>
      <text className="dg-note" x={20} y={210}>embeddings have no</text>
      <text className="dg-note" x={20} y={230}>randomness</text>
      <text className="dg-note" x={20} y={262}>cost: 15 tiny embedding</text>
      <text className="dg-note" x={20} y={282}>requests</text>
      <Box x={228} y={4} w={206} h={300} label="" />
      <text className="dg-label" x={240} y={28}>answers, with a judge</text>
      <text className="dg-note" x={240} y={56}>RelevancyEvaluator,</text>
      <text className="dg-note" x={240} y={78}>its own ChatClient: YES or NO</text>
      <text className="dg-note" x={240} y={112}>ticket for a child: YES</text>
      <text className="dg-note" x={240} y={134}>which exhibits?: NO</text>
      <text className="dg-note" x={240} y={156}>T-rex: YES, then NO on</text>
      <text className="dg-note" x={240} y={178}>a re-run (a vaguer answer)</text>
      <text className="dg-note" x={240} y={230}>answers and verdicts vary:</text>
      <text className="dg-note" x={240} y={252}>read the rate over many</text>
      <text className="dg-note" x={240} y={274}>questions</text>
      <text className="dg-note" x={8} y={324}>Measured on 26 November with the real models.</text>
    </Svg>
  );
}

function AiGuardrails() {
  // Still (owner, 26 November): chapter 17's three real questions, with the tokens the gateway counted.
  const rows: [string, string, string, BoxTone][] = [
    ["my phone number is 98220 12345", "SafeGuardAdvisor refuses", "0 tokens", "highlight"],
    ["a 336-character attack", "QuestionLimitAdvisor refuses", "0 tokens", "highlight"],
    ["my number is 98220 12345, call me", "passes both guards: the model", "132 tokens", "plain"],
  ];
  return (
    <Svg viewBox="0 0 440 290" label="Three real questions: the phone number and the long attack were refused by guards with zero tokens; my number is passed the word list and reached the model, 132 tokens">
      {rows.map(([q, what, cost, tone], i) => {
        const y = 4 + i * 86;
        return (
          <g key={i}>
            <Box x={8} y={y} w={426} h={72} label="" tone={tone} />
            <text className="dg-label" x={20} y={y + 24}>{q}</text>
            <text className="dg-note" x={20} y={y + 50}>{what}</text>
            <text className="dg-label" x={420} y={y + 50} textAnchor="end">{cost}</text>
          </g>
        );
      })}
      <text className="dg-note" x={8} y={282}>The third shows the limit of a word list: the number left the museum.</text>
    </Svg>
  );
}

function AiCostMeter() {
  // Still (owner, 26 November): chapter 18's real meter and metrics.
  const rows: [string, string, BoxTone][] = [
    ["one answer: When are you open?", "usage from the provider: 95 in, 27 out", "plain"],
    ["your code prices it", "95 x $0.15/M + 27 x $0.60/M = $0.00003045", "accent"],
    ["Spring AI counts every call", "metric gen_ai.client.token.usage", "copy"],
    ["/actuator/metrics, after 3 answers", "input 296, output 131, total 427", "copy"],
    ["no tag chosen?", "854: every token counted twice. Pick a type.", "highlight"],
  ];
  return (
    <Svg viewBox="0 0 440 374" label="One answer's usage, 95 in and 27 out, priced at 0.00003045 dollars; Spring AI's metric after three answers: input 296, output 131, total 427, and 854 without a tag">
      {rows.map(([title, detail, tone], i) => {
        const y = 4 + i * 74;
        return (
          <g key={i}>
            <Box x={28} y={y} w={406} h={56} label="" tone={tone} />
            <text className="dg-label" x={42} y={y + 22}>{title}</text>
            <text className="dg-note" x={42} y={y + 43}>{detail}</text>
            {i < rows.length - 1 && <Arrow x1={231} y1={y + 58} x2={231} y2={y + 72} />}
          </g>
        );
      })}
    </Svg>
  );
}

function AiWorkflows() {
  // Still (owner, 26 November): chapter 19's two real workflows.
  return (
    <Svg viewBox="0 0 440 350" label="Routing: Are you open on Sunday goes to the VISIT desk, which answers with the hours. Review loop: the writer drafts, the reviewer says more than 40 words although the label has about 30, the writer rewrites, and the loop stops at three drafts">
      <Box x={8} y={4} w={204} h={318} label="" tone="accent" />
      <text className="dg-label" x={20} y={28}>routing: 2 calls</text>
      <Box x={20} y={42} w={180} h={44} label="Open on Sunday?" />
      <Arrow x1={110} y1={88} x2={110} y2={104} />
      <Box x={20} y={106} w={180} h={44} label="router: VISIT" tone="copy" />
      <Arrow x1={110} y1={152} x2={110} y2={168} />
      <Box x={20} y={170} w={180} h={44} label="the VISIT desk's prompt" />
      <Arrow x1={110} y1={216} x2={110} y2={232} />
      <text className="dg-note" x={20} y={256}>Yes, open on Sunday</text>
      <text className="dg-note" x={20} y={276}>from 10:00 to 18:00.</text>
      <Box x={228} y={4} w={206} h={318} label="" />
      <text className="dg-label" x={240} y={28}>review loop: up to 6 calls</text>
      <Box x={240} y={42} w={182} h={44} label="writer: a draft" tone="copy" />
      <Arrow x1={331} y1={88} x2={331} y2={104} />
      <Box x={240} y={106} w={182} h={58} label="" tone="highlight" />
      <text className="dg-note" x={250} y={128}>reviewer: more than 40</text>
      <text className="dg-note" x={250} y={150}>words (it had about 30)</text>
      <Arrow x1={331} y1={166} x2={331} y2={182} />
      <Box x={240} y={184} w={182} h={44} label="writer: rewrite" tone="copy" />
      <text className="dg-note" x={240} y={256}>3 drafts, never approved:</text>
      <text className="dg-note" x={240} y={276}>the limit ended the loop.</text>
      <text className="dg-note" x={240} y={298}>Count words in Java.</text>
      <text className="dg-note" x={8} y={344}>Both measured on 26 November with the real model.</text>
    </Svg>
  );
}

function AiAtlasLive() {
  // Still (owner, 26 November): one real message of chapter 20's conversation, through every piece.
  const rows: [string, string, BoxTone][] = [
    ["Ria: What shows are there that day?", "POST /chat", "plain"],
    ["guards (HIGHEST_PRECEDENCE)", "no private words, under 300 characters: pass", "highlight"],
    ["session memory", "adds her earlier turns: \"this Saturday\" = 2026-11-28", "accent"],
    ["retrieval (top 3, 0.35)", "no card close enough: sources []", "accent"],
    ["the model, with tools", "planetariumShows {date: 2026-11-28}", "copy"],
    ["the answer", "11:00: 4 free, 14:00: fully booked, 16:00: 11 free", "plain"],
  ];
  return (
    <Svg viewBox="0 0 440 448" label="Ria's question what shows are there that day passes the guards, gains her session's history, finds no card, and the model calls planetariumShows for 2026-11-28 and answers with the seats">
      {rows.map(([title, detail, tone], i) => {
        const y = 4 + i * 74;
        return (
          <g key={i}>
            <Box x={28} y={y} w={406} h={56} label="" tone={tone} />
            <text className="dg-label" x={42} y={y + 22}>{title}</text>
            <text className="dg-note" x={42} y={y + 43}>{detail}</text>
            {i < rows.length - 1 && <Arrow x1={231} y1={y + 58} x2={231} y2={y + 72} />}
          </g>
        );
      })}
    </Svg>
  );
}

function L4jAiCircles() {
  // Still (owner, 26 November): each field inside the one before, with Setu's own example of each.
  const rings: [number, string, string, string][] = [
    [0, "Artificial intelligence", "any program doing something we call intelligent", "Setu's hand-written rules (this chapter)"],
    [1, "Machine learning", "the rule is learned from examples", "the 12-minute threshold (this chapter)"],
    [2, "Deep learning", "learning with neural networks of many layers", "reading a photo of a ticket"],
    [3, "Generative AI", "models that create new text, images or code", "writing a polite reply to a passenger"],
  ];
  const inset = 22, top = 70;
  return (
    <Svg viewBox="0 0 440 420" label="Artificial intelligence contains machine learning, which contains deep learning, which contains generative AI; a large language model sits inside generative AI">
      {rings.map(([i, name, means, eg]) => {
        const x = i * inset, y = i * top, w = 440 - 2 * x, h = 418 - y - i * 12;
        return (
          <g key={name}>
            <g className={`dg-box dg-${i === 3 ? "accent" : i % 2 ? "copy" : "plain"}`}><rect x={x + 1} y={y + 1} width={w - 2} height={h - 2} rx={18} /></g>
            <text className="dg-label" x={x + 14} y={y + 22}>{name}</text>
            <text className="dg-note" x={x + 14} y={y + 40}>{means}</text>
            <text className="dg-note" x={x + 14} y={y + 58} style={{ opacity: 0.75 }}>e.g. {eg}</text>
          </g>
        );
      })}
      <Box x={90} y={300} w={260} h={44} label="a large language model (Setu's)" tone="highlight" />
      <text className="dg-note" x={220} y={364} textAnchor="middle">it sits in all four circles at once</text>
    </Svg>
  );
}

function L4jBigramChain() {
  // Still (owner, 26 November): chapter 3's real generated sentence, each step with the count that chose it.
  const steps: [string, string][] = [
    ["the", "ghat: 3 of 7"], ["ghat", "express: 3 of 3"], ["express", "to: 2 of 3"], ["to", "lonavala: 3 of 6"],
    ["lonavala", "will: 2 of 3"], ["will", "leave: 2 of 3"], ["leave", "from: 2 of 2"], ["from", "platform: 2 of 2"],
    ["platform", "one: 2 of 3"], ["one", "stop: no follower"],
  ];
  return (
    <Svg viewBox="0 0 440 420" label="The bigram model generates: the, ghat, express, to, lonavala, will, leave, from, platform, one; each next word is the most frequent follower in the eight announcements, and nothing ever followed one">
      {steps.map(([word, next], i) => {
        const col = i < 5 ? 0 : 1, row = i % 5;
        const x = 8 + col * 220, y = 8 + row * 80;
        return (
          <g key={word}>
            <Box x={x} y={y} w={96} h={40} label={word} tone={i === 9 ? "highlight" : "copy"} code />
            <text className="dg-note" x={x + 104} y={y + 25}>{next}</text>
            {row < 4 && <Arrow x1={x + 48} y1={y + 42} x2={x + 48} y2={y + 78} />}
          </g>
        );
      })}
      <text className="dg-note" x={8} y={412}>Read down the left column, then the right.</text>
    </Svg>
  );
}

function L4jGrounding() {
  // Still (owner, 26 November): chapter 11's real answers at temperature 0, against timetable.txt.
  const rows: [string, string, BoxTone][] = [
    ["Ghat Express leaves Pune?", "no facts: 6:00 AM (wrong); with facts: 07:15; true: 07:15", "highlight"],
    ["Pune to Karjat fare?", "no facts: check the website; with facts: Rs 140; true: Rs 140", "plain"],
    ["Konkan Breeze on Tuesdays?", "no facts: yes (wrong); with facts: no; true: no", "highlight"],
    ["wifi on the Monsoon Mail?", "with facts: I don't know (it is not in the facts)", "copy"],
  ];
  return (
    <Svg viewBox="0 0 440 300" label="Without facts the model said 6:00 AM and yes for Tuesdays, both wrong; with the timetable in the prompt it said 07:15, Rs 140, no, and I don't know for wifi">
      {rows.map(([q, detail, tone], i) => {
        const y = 4 + i * 66;
        return (
          <g key={q}>
            <Box x={4} y={y} w={432} h={56} label="" tone={tone} />
            <text className="dg-label" x={16} y={y + 22}>{q}</text>
            <text className="dg-note" x={16} y={y + 43}>{detail}</text>
          </g>
        );
      })}
      <text className="dg-note" x={8} y={290}>Temperature 0: the same wrong answers on every run, days apart.</text>
    </Svg>
  );
}

function L4jStructured() {
  // Still (owner, 26 November): chapter 15's real extraction, run twice with the same result.
  const rows: [string, string, BoxTone][] = [
    ["the passenger's message", "3 tickets from Pune to Karjat this coming Saturday", "plain"],
    ["the JSON schema, strict", "from, to, date (YYYY-MM-DD), passengers", "accent"],
    ["the model's JSON", "{\"from\":\"Pune\",\"to\":\"Karjat\",\"date\":\"2026-11-26\",\"passengers\":3}", "plain"],
    ["a TripRequest record", "trip.passengers() + 1 = 4", "copy"],
    ["but the date", "2026-11-26 is a Thursday; Saturday is 2026-11-28", "highlight"],
  ];
  return (
    <Svg viewBox="0 0 440 374" label="The message goes to the model with a strict schema; the JSON fits the schema and becomes a TripRequest, but the date it chose is a Thursday, not Saturday">
      {rows.map(([title, detail, tone], i) => {
        const y = 4 + i * 74;
        return (
          <g key={i}>
            <Box x={28} y={y} w={406} h={56} label="" tone={tone} />
            <text className="dg-label" x={42} y={y + 22}>{title}</text>
            <text className="dg-note" x={42} y={y + 43}>{detail}</text>
            {i < rows.length - 1 && <Arrow x1={231} y1={y + 58} x2={231} y2={y + 72} />}
          </g>
        );
      })}
    </Svg>
  );
}

function L4jNeuron() {
  // Still (owner, 26 November): chapter 2's trained neuron (weights 0.1, 0.2, 0.3, bias -0.2) on one morning.
  const inputs: [string, string, string, number][] = [["rain", "0", "x 0.1", 0], ["holiday", "1", "x 0.2", 0.2], ["track work", "1", "x 0.3", 0.3]];
  return (
    <Svg viewBox="0 0 440 300" label="Rain 0, holiday 1 and track work 1 are multiplied by the weights 0.1, 0.2 and 0.3; with the bias of minus 0.2 the total is 0.3, above zero, so the neuron fires: late">
      {inputs.map(([name, v, w, part], i) => {
        const y = 10 + i * 72;
        return (
          <g key={name}>
            <Box x={8} y={y} w={140} h={56} label="" />
            <text className="dg-label" x={20} y={y + 23}>{name} = {v}</text>
            <text className="dg-note" x={20} y={y + 44}>{w} = {part}</text>
            <line className="dg-arrow" x1={150} y1={y + 28} x2={238} y2={118} markerEnd="var(--figure-arrowhead)" />
          </g>
        );
      })}
      <Box x={240} y={86} w={192} h={64} label="0 + 0.2 + 0.3 - 0.2 = 0.3" tone="accent" />
      <text className="dg-note" x={248} y={170}>the bias, -0.2, is added too</text>
      <Arrow x1={336} y1={176} x2={336} y2={212} />
      <Box x={240} y={214} w={192} h={50} label="0.3 > 0: fires, late" tone="copy" />
      <text className="dg-note" x={8} y={292}>The weights and the bias came from training on eight mornings.</text>
    </Svg>
  );
}

function L4jContextWindow() {
  // Still (owner, 26 November): chapter 4's real chat, counted with o200k_base, fitted into a 40-token budget.
  const rows: [string, number, string, boolean][] = [
    ["Passenger: Can she get a lower berth?", 9, "9", true],
    ["Setu: The Ghat Express leaves Pune at 7:15 ...", 25, "34", true],
    ["Passenger: We want the morning train ...", 14, "48: over 40, stop", false],
    ["Setu: Hello! How can I help you plan ...", 14, "not looked at", false],
    ["Passenger: Hello! I am travelling with my ...", 13, "not looked at", false],
  ];
  return (
    <Svg viewBox="0 0 440 330" label="Walking from the newest message back: 9 tokens, then 25 for a total of 34; the next, 14 tokens, would make 48, over the budget of 40, so the walk stops; only the last two messages are sent">
      <text className="dg-label" x={8} y={16}>newest first</text>
      <text className="dg-label" x={432} y={16} textAnchor="end">tokens, running total</text>
      {rows.map(([msg, t, total, kept], i) => {
        const y = 26 + i * 58;
        return (
          <g key={i} opacity={kept ? 1 : 0.55}>
            <Box x={8} y={y} w={426} h={48} label="" tone={kept ? "copy" : "plain"} />
            <text className="dg-note" x={18} y={y + 20}>{msg}</text>
            <text className="dg-note" x={18} y={y + 39}>{t} tokens</text>
            <text className="dg-label" x={424} y={y + 39} textAnchor="end">{total}</text>
          </g>
        );
      })}
      <text className="dg-note" x={8} y={322}>Sent, oldest first: only the two green messages.</text>
    </Svg>
  );
}

function L4jEmbeddingSpace() {
  // Still (owner, 26 November): chapter 5's real cosine scores from BGE small (384 numbers per text).
  const pairs: [string, number, boolean][] = [
    ["dog ~ puppy", 0.862, true], ["refund ~ money back", 0.763, true],
    ["dog ~ platform", 0.612, false], ["refund ~ luggage", 0.564, false],
  ];
  return (
    <Svg viewBox="0 0 440 250" label="Real cosine scores: dog and puppy 0.862, refund and money back 0.763, dog and platform 0.612, refund and luggage 0.564; related pairs score higher, but unrelated pairs are far from zero">
      {pairs.map(([name, score, related], i) => {
        const y = 10 + i * 48;
        const w = score * 260;
        return (
          <g key={name}>
            <text className="dg-note" x={8} y={y + 22}>{name}</text>
            <Box x={160} y={y} w={w} h={32} label="" tone={related ? "copy" : "plain"} />
            <text className="dg-note" x={168 + w} y={y + 22}>{score.toFixed(3)}</text>
          </g>
        );
      })}
      <text className="dg-note" x={8} y={222}>Related pairs score higher, but unrelated ones are not near 0:</text>
      <text className="dg-note" x={8} y={242}>with this model, compare scores, never trust one alone.</text>
    </Svg>
  );
}

function L4jAttention() {
  // Still (owner, 26 November): chapter 6's real attention weights for "it" (hand-written 3-number vectors).
  const bars: [string, number][] = [["train", 0.46], ["it", 0.36], ["station", 0.18]];
  return (
    <Svg viewBox="0 0 440 230" label="The query of it is compared with each key; after softmax, it gives the train 0.46 of its attention, itself 0.36 and the station 0.18">
      <text className="dg-label" x={8} y={18}>where "it" puts its attention</text>
      {bars.map(([word, w], i) => {
        const y = 34 + i * 50;
        return (
          <g key={word}>
            <text className="dg-note" x={8} y={y + 22}>{word}</text>
            <Box x={90} y={y} w={w * 600} h={32} label="" tone={i === 0 ? "copy" : "plain"} />
            <text className="dg-note" x={98 + w * 600} y={y + 22}>{w.toFixed(2)}</text>
          </g>
        );
      })}
      <text className="dg-note" x={8} y={204}>score = query . key / sqrt(3), then softmax:</text>
      <text className="dg-note" x={8} y={224}>the weights add up to 1.00.</text>
    </Svg>
  );
}

function L4jLlmPipeline() {
  // Still (owner, 26 November): how gpt-4o-mini answers, with this course's real numbers where they exist.
  const rows: [string, string, BoxTone][] = [
    ["1. tokens (chapter 4)", "When does the Ghat Express leave Pune? = 9 tokens", "plain"],
    ["2. embeddings (chapter 5)", "each token becomes a vector of numbers", "plain"],
    ["3. layers of attention (this chapter)", "each token looks at all the tokens before it", "accent"],
    ["4. scores", "one for each of about 200,000 possible next tokens", "accent"],
    ["5. softmax and temperature", "e.g. late 0.73 at temperature 1; one token is sampled", "copy"],
    ["6. repeat", "add the token, run the model again, until an end token", "plain"],
  ];
  return (
    <Svg viewBox="0 0 440 448" label="How a language model answers: tokens, embeddings, layers of attention, scores for every possible next token, softmax and temperature pick one, and the loop repeats">
      {rows.map(([title, detail, tone], i) => {
        const y = 4 + i * 74;
        return (
          <g key={i}>
            <Box x={28} y={y} w={406} h={56} label="" tone={tone} />
            <text className="dg-label" x={42} y={y + 22}>{title}</text>
            <text className="dg-note" x={42} y={y + 43}>{detail}</text>
            {i < rows.length - 1 && <Arrow x1={231} y1={y + 58} x2={231} y2={y + 72} />}
          </g>
        );
      })}
    </Svg>
  );
}

function L4jHttpCall() {
  // Still (owner, 26 November): chapter 7's real call, from the program and the gateway's log.
  const rows: [string, string, BoxTone][] = [
    ["Setu builds the JSON body", "model ai-chat; a system and a user message", "plain"],
    ["POST $OPENAI_BASE_URL/chat/completions", "Authorization: Bearer (your lab key), HTTP/1.1", "accent"],
    ["the LabBox gateway", "checks the budget, adds max_tokens 1024 and the real key", "accent"],
    ["OpenAI: gpt-4o-mini-2024-07-18", "reads 62 tokens, writes 55", "copy"],
    ["JSON back to Setu", "choices[0].message.content; finish_reason stop", "plain"],
  ];
  return (
    <Svg viewBox="0 0 440 374" label="Setu builds a JSON body, posts it with its lab key to the gateway, the gateway forwards it to gpt-4o-mini with the real key, and the JSON answer comes back">
      {rows.map(([title, detail, tone], i) => {
        const y = 4 + i * 74;
        return (
          <g key={i}>
            <Box x={28} y={y} w={406} h={56} label="" tone={tone} />
            <text className="dg-label" x={42} y={y + 22}>{title}</text>
            <text className="dg-note" x={42} y={y + 43}>{detail}</text>
            {i < rows.length - 1 && <Arrow x1={231} y1={y + 58} x2={231} y2={y + 72} />}
          </g>
        );
      })}
    </Svg>
  );
}

function L4jAiService() {
  // Still (owner, 26 November): chapter 13's real call, from the program and the gateway's log.
  const rows: [string, string, BoxTone][] = [
    ["setu.chat(\"Hello!\")", "your code calls the interface", "plain"],
    ["the proxy: jdk.proxy3.$Proxy28", "made by the JDK at run time; nobody wrote it", "accent"],
    ["reads @SystemMessage(fromResource=...)", "setu-system.txt, sent with its final newline", "accent"],
    ["builds the messages, calls the ChatModel", "system: the file's text; user: Hello!", "copy"],
    ["converts the answer", "a String: Hello! I'm Setu, the help desk assistant ...", "plain"],
  ];
  return (
    <Svg viewBox="0 0 440 374" label="A call to setu.chat goes to a proxy made at run time; it reads the annotation, builds the system and user messages, calls the ChatModel and returns the answer as a String">
      {rows.map(([title, detail, tone], i) => {
        const y = 4 + i * 74;
        return (
          <g key={i}>
            <Box x={28} y={y} w={406} h={56} label="" tone={tone} />
            <text className="dg-label" x={42} y={y + 22}>{title}</text>
            <text className="dg-note" x={42} y={y + 43}>{detail}</text>
            {i < rows.length - 1 && <Arrow x1={231} y1={y + 58} x2={231} y2={y + 72} />}
          </g>
        );
      })}
    </Svg>
  );
}

function L4jToolCall() {
  // Still (owner, 26 November): chapter 19's real exchange, from the gateway's log.
  const rows: [string, string, BoxTone][] = [
    ["the question + the tool descriptions", "3 tickets Pune to Karjat this coming Saturday", "plain"],
    ["model call 1 (194 tokens in): no text", "asks for nextDate(SATURDAY) and fare(Karjat)", "accent"],
    ["LangChain4j runs your Java", "2026-11-28 and 140", "copy"],
    ["model call 2 (263 tokens in)", "the results are in the conversation now", "accent"],
    ["the answer", "Saturday is November 28, 2026; 3 tickets cost Rs 420", "plain"],
  ];
  return (
    <Svg viewBox="0 0 440 374" label="The model asks for two tools in one reply, Java runs them and returns 2026-11-28 and 140, and the second model call writes the answer with the right date and Rs 420">
      {rows.map(([title, detail, tone], i) => {
        const y = 4 + i * 74;
        return (
          <g key={i}>
            <Box x={28} y={y} w={406} h={56} label="" tone={tone} />
            <text className="dg-label" x={42} y={y + 22}>{title}</text>
            <text className="dg-note" x={42} y={y + 43}>{detail}</text>
            {i < rows.length - 1 && <Arrow x1={231} y1={y + 58} x2={231} y2={y + 72} />}
          </g>
        );
      })}
    </Svg>
  );
}

function L4jRag() {
  // Still (owner, 26 November): chapter 23's real run, piece count, scores and tokens from the gateway's log.
  const once: string[] = ["5 files", "12 pieces", "412 tokens"];
  const ask: [string, BoxTone][] = [
    ["\"Can I bring my guitar?\" embedded: 6 tokens", "plain"],
    ["best piece 0.711: \"Musical instruments up to 1.5 m...\"", "accent"],
    ["next best 0.641: below 0.7, left out", "plain"],
    ["1 piece + question + rules: 107 tokens in", "plain"],
    ["\"Yes ... up to 1.5 metres ... free\"", "copy"],
  ];
  return (
    <Svg viewBox="0 0 440 452" label="Indexing once: five files of 1,772 characters became 12 pieces, embedded in one call of 412 tokens. For the guitar question: the question is embedded, the musical instruments piece scores 0.711, the next 0.641 is left out, the request is 107 tokens, and the answer quotes the 1.5 metre rule">
      <text className="dg-label" x={8} y={18}>indexing, once</text>
      {once.map((t, i) => (
        <g key={t}>
          <Box x={8 + i * 146} y={28} w={132} h={52} label={t} tone="plain" />
          {i < 2 && <Arrow x1={140 + i * 146} y1={54} x2={154 + i * 146} y2={54} />}
        </g>
      ))}      <text className="dg-note" x={8} y={100}>1,772 characters, cut at 300, embedded in one call</text>
      <text className="dg-label" x={8} y={124}>retrieval, every question</text>
      {ask.map(([t, tone], i) => (
        <g key={t}>
          <Box x={8} y={134 + i * 58} w={424} h={42} label={t} tone={tone} />
          {i < ask.length - 1 && <Arrow x1={220} y1={176 + i * 58} x2={220} y2={192 + i * 58} />}
        </g>
      ))}
      <text className="dg-note" x={8} y={444}>Of 12 pieces, one sentence travelled with the question.</text>
    </Svg>
  );
}

function L4jSequence() {
  // Still (owner, 26 November): chapter 27's real run, the scope after each step; tokens from the gateway's log.
  const steps: [string, string, string, BoxTone][] = [
    ["desk.handle(message)", "", "message", "plain"],
    ["classifier", "56 in, 2 out", "message, topic = REFUND", "accent"],
    ["writer", "270 in, 24 out", "message, topic, reply", "copy"],
  ];
  return (
    <Svg viewBox="0 0 440 276" label="The refund message: the workflow puts message in the scope; the classifier, 56 tokens in and 2 out, adds topic REFUND; the writer, 270 tokens in and 24 out, reads both and adds reply, which the workflow returns">
      <text className="dg-label" x={8} y={18}>step</text>
      <text className="dg-label" x={218} y={18}>the scope afterwards</text>
      {steps.map(([step, cost, scope, tone], i) => {
        const y = 28 + i * 74;
        return (
          <g key={step}>
            <Box x={8} y={y} w={190} h={46} label={step} tone={tone} />
            {cost && <text className="dg-note" x={14} y={y + 62}>{cost}</text>}
            <Arrow x1={198} y1={y + 23} x2={214} y2={y + 23} />
            <Box x={214} y={y} w={218} h={46} label={scope} tone="plain" />
          </g>
        );
      })}
      <text className="dg-note" x={8} y={268}>The workflow returns "reply". Code fixed the order.</text>
    </Svg>
  );
}

function L4jWorkflow() {
  // Still (owner, 26 November): chapter 28's real run, one row per model call, from the trace.
  const runs: [string, [string, BoxTone][]][] = [
    ["refund question: 3 calls", [["classify", "plain"], ["refund desk", "accent"], ["score 0.8+", "copy"]]],
    ["timetable question: 3 calls", [["classify", "plain"], ["timetable desk", "accent"], ["score 0.8+", "copy"]]],
    ["bad reply, loop only: 3 calls", [["score: low", "highlight"], ["edit", "accent"], ["score 0.8", "copy"]]],
    ["strict scorer, ceiling 3: 6 calls", [["score, edit", "highlight"], ["score, edit", "highlight"], ["score, edit: stop", "highlight"]]],
  ];
  return (
    <Svg viewBox="0 0 440 352" label="Real runs: the refund and timetable questions each took three calls, classify, desk and one passing score; the bad reply took score, edit and a passing score; a scorer that could never pass stopped after three rounds of score and edit, six calls">
      {runs.map(([title, cells], r) => {
        const y = 6 + r * 82;
        return (
          <g key={title}>
            <text className="dg-label" x={8} y={y + 14}>{title}</text>
            {cells.map(([t, tone], c) => (
              <g key={c}>
                <Box x={8 + c * 146} y={y + 24} w={132} h={40} label={t} tone={tone} />
                {c < 2 && <Arrow x1={140 + c * 146} y1={y + 44} x2={154 + c * 146} y2={y + 44} />}
              </g>
            ))}
          </g>
        );
      })}
      <text className="dg-note" x={8} y={344}>Code picked every path; maxIterations(3) capped the last one.</text>
    </Svg>
  );
}

function L4jStreaming() {
  // Still (owner, 26 November): chapter 16's measured run (56 pieces; first after 905 ms, all after 2103 ms).
  const x0 = 96, px = 130; // 130 px a second
  const t = (sec: number) => x0 + sec * px;
  return (
    <Svg viewBox="0 0 440 250" label="Without streaming the screen stays empty until 2.1 seconds; with streaming the first piece arrives at 0.9 seconds and the rest follow until 2.1 seconds">
      {[0, 1, 2].map((sec) => (
        <g key={sec}>
          <line className="dg-arrow" x1={t(sec)} y1={30} x2={t(sec)} y2={186} strokeDasharray="3 4" />
          <text className="dg-note" x={t(sec) - 8} y={206}>{sec} s</text>
        </g>
      ))}
      <text className="dg-label" x={8} y={66}>no stream</text>
      <Box x={t(0)} y={44} w={2.103 * px} h={34} label="empty box" />
      <Box x={t(2.103)} y={44} w={40} h={34} label="all" tone="copy" />
      <text className="dg-label" x={8} y={136}>stream</text>
      <Box x={t(0)} y={114} w={0.905 * px} h={34} label="empty" />
      <Box x={t(0.905)} y={114} w={1.198 * px} h={34} label="56 pieces arrive" tone="copy" />
      <text className="dg-note" x={8} y={236}>Same total time; the passenger starts reading after 0.9 s.</text>
    </Svg>
  );
}

function L4jMemoryWindow() {
  // Still (owner, 26 November): a real MessageWindowChatMemory(10) after a system message and 6 questions and answers.
  const msgs: [string, boolean][] = [
    ["SYS", true], ["q1", false], ["a1", false], ["q2", false], ["a2", true], ["q3", true], ["a3", true],
    ["q4", true], ["a4", true], ["q5", true], ["a5", true], ["q6", true], ["a6", true],
  ];
  return (
    <Svg viewBox="0 0 440 200" label="Thirteen messages were added to a window of ten: the system message stays, q1, a1 and q2 are evicted, and the window starts with a2, an answer whose question is gone">
      <text className="dg-label" x={8} y={18}>added: 1 system message + 6 questions and answers = 13</text>
      {msgs.map(([m, kept], i) => (
        <g key={m} opacity={kept ? 1 : 0.4}>
          <Box x={8 + i * 33} y={34} w={30} h={40} label={m === "SYS" ? "S" : m} tone={m === "SYS" ? "accent" : kept ? "copy" : "plain"} code />
        </g>
      ))}
      <text className="dg-note" x={8} y={102}>kept: 10 (the system message counts as one of them)</text>
      <text className="dg-note" x={8} y={124}>evicted: q1, a1, q2 (faded)</text>
      <text className="dg-note" x={8} y={152}>The kept history starts with a2: an answer whose question</text>
      <text className="dg-note" x={8} y={172}>is gone. S = the system message, never evicted.</text>
    </Svg>
  );
}

function L4jRouting() {
  // Still (owner, 26 November): chapter 24's real routed run, max_tokens and token counts from the gateway's log.
  const rows: [string, string, string, BoxTone][] = [
    ["\"Hi!\" (3 characters)", "simple: max 60 tokens", "9 in, 9 out", "plain"],
    ["complaint (197 characters)", "complex: max 400 tokens", "52 in, 274 out", "accent"],
  ];
  return (
    <Svg viewBox="0 0 440 270" label="The router measured each message: Hi, three characters, went to the simple route with at most 60 tokens and used 9 in and 9 out; the 197-character complaint went to the complex route with at most 400 tokens and used 52 in and 274 out">
      <text className="dg-label" x={8} y={18}>one RoutingChatModel, rule: over 120 characters is complex</text>
      {rows.map(([msg, route, used, tone], i) => {
        const y = 32 + i * 116;
        return (
          <g key={msg}>
            <Box x={8} y={y} w={424} h={36} label={msg} tone="plain" />
            <Arrow x1={110} y1={y + 36} x2={110} y2={y + 50} />
            <Box x={8} y={y + 50} w={204} h={36} label={route} tone={tone} />
            <Arrow x1={212} y1={y + 68} x2={228} y2={y + 68} />
            <Box x={228} y={y + 50} w={204} h={36} label={used} tone="copy" />
          </g>
        );
      })}
      <text className="dg-note" x={8} y={262}>Both routes are ai-chat here, with different limits.</text>
    </Svg>
  );
}

function L4jMcpWire() {
  // Still (owner, 26 November): chapter 21's real stdio traffic, copied from tee logs of both streams.
  const rows: [string, string, BoxTone][] = [
    ["discover (2026-07-28)", "Method not found", "highlight"],
    ["initialize (2025-11-25)", "sahyadri-rail 1.0.0", "plain"],
    ["tools/list", "fare, nextDate", "plain"],
    ["tools/call fare Ratnagiri", "\"420\"", "copy"],
  ];
  return (
    <Svg viewBox="0 0 440 360" label="The real messages between Setu and the rail server: a protocol detection request the server does not know, then initialize, tools/list and a tools/call of fare for Ratnagiri answered with 420">
      <text className="dg-label" x={8} y={20}>client writes to stdin</text>
      <text className="dg-label" x={256} y={20}>server writes to stdout</text>
      {rows.map(([ask, answer, tone], i) => (
        <g key={i}>
          <Box x={8} y={34 + i * 74} w={196} h={48} label={ask} tone="accent" />
          <Arrow x1={204} y1={52 + i * 74} x2={252} y2={52 + i * 74} />
          <Arrow x1={252} y1={66 + i * 74} x2={204} y2={66 + i * 74} />
          <Box x={252} y={34 + i * 74} w={180} h={48} label={answer} tone={tone} />
        </g>
      ))}
      <text className="dg-note" x={8} y={334}>One JSON object per line; an answer repeats its request id.</text>
      <text className="dg-note" x={8} y={352}>The client tries the newest version first, then falls back.</text>
    </Svg>
  );
}

function L4jMcp() {
  // Still (owner, 26 November): chapter 20's real runs, 14 tools against 2, from the gateway's log.
  const left: [string, BoxTone][] = [
    ["all 14 tools offered", "plain"], ["1,222 tokens in", "plain"], ["search_files by name", "accent"],
    ["file names only: nothing", "plain"], ["\"no notices\": wrong", "highlight"],
  ];
  const right: [string, BoxTone][] = [
    ["2 tools offered", "plain"], ["305 tokens in", "plain"], ["list_directory", "accent"],
    ["read_text_file x 3, at once", "accent"], ["40 min late: right", "copy"],
  ];
  const col = (items: [string, BoxTone][], x: number) => items.map(([t, tone], i) => (
    <g key={x + i}>
      <Box x={x} y={34 + i * 62} w={206} h={44} label={t} tone={tone} />
      {i < items.length - 1 && <Arrow x1={x + 103} y1={80 + i * 62} x2={x + 103} y2={94 + i * 62} />}
    </g>
  ));
  return (
    <Svg viewBox="0 0 440 370" label="With all fourteen filesystem tools the model used search_files on file names, found nothing and answered wrongly; with two tools it listed the folder, read the three notices and answered right, with far fewer tokens">
      <text className="dg-label" x={8} y={20}>the same question, two tool sets</text>
      {col(left, 8)}
      {col(right, 226)}
      <text className="dg-note" x={8} y={362}>Fewer tools: safer, cheaper, and here the only right answer.</text>
    </Svg>
  );
}

function L4jVectorSearch() {
  // Still (owner, 26 November): chapter 22's real scores for every card, text-embedding-3-small, no threshold.
  const groups: [string, [string, number][]][] = [
    ["Can I take my bicycle?", [["Luggage", 0.712], ["Lost property", 0.645], ["Pets", 0.612], ["Accessibility", 0.608], ["Refunds", 0.578], ["Monsoon", 0.573]]],
    ["What is the capital of France?", [["Accessibility", 0.543], ["Lost property", 0.538], ["Luggage", 0.526], ["Monsoon", 0.523], ["Refunds", 0.523], ["Pets", 0.515]]],
  ];
  const x0 = 110, scale = 280, cut = x0 + 0.7 * scale;
  return (
    <Svg viewBox="0 0 440 410" label="Scores of all six cards: for the bicycle question Luggage 0.712 is the only one at or above 0.7; for the France question the best is Accessibility at 0.543, so nothing passes the 0.7 threshold">
      {groups.map(([q, rows], g) => {
        const top = 4 + g * 178;
        return (
          <g key={q}>
            <text className="dg-label" x={8} y={top + 14}>{q}</text>
            {rows.map(([card, score], i) => {
              const y = top + 24 + i * 24;
              return (
                <g key={card}>
                  <text className="dg-note" x={8} y={y + 14}>{card}</text>
                  <Box x={x0} y={y} w={score * scale} h={18} label="" tone={score >= 0.7 ? "copy" : "plain"} />
                  <text className="dg-note" x={384} y={y + 14}>{score.toFixed(3)}</text>
                </g>
              );
            })}
            <line className="dg-arrow" x1={cut} y1={top + 20} x2={cut} y2={top + 172} strokeDasharray="3 4" />
          </g>
        );
      })}
      <text className="dg-note" x={cut - 8} y={372}>0.7</text>
      <text className="dg-note" x={8} y={390}>Score = (cosine + 1) / 2, so 0.5 means unrelated.</text>
      <text className="dg-note" x={8} y={406}>Only Luggage reaches 0.7; France gets nothing.</text>
    </Svg>
  );
}

function L4jEval() {
  // Still (owner, 26 November): chapter 26's real eval runs, full prompt against the prompt without two rules.
  const rows: [string, string, BoxTone][] = [
    ["full system message", "6 of 6 passed, 1,418 tokens in", "copy"],    ["two rules removed, run 1", "5 of 6: honest, other words", "plain"],
    ["two rules removed, run 2", "5 of 6: invented \"no wi-fi\"", "highlight"],
    ["two rules removed, run 3", "5 of 6: invented \"no wi-fi\"", "highlight"],
    ["two rules removed, run 4", "5 of 6: honest, other words", "plain"],
  ];
  return (
    <Svg viewBox="0 0 440 340" label="With the full system message the golden set passed 6 of 6 at 1,418 tokens in. Without the two rules it scored 5 of 6 in all four runs: twice the model invented that there is no wi-fi, twice it answered honestly in other words that the simple check did not accept">
      <text className="dg-label" x={8} y={18}>the golden set, same six questions</text>
      {rows.map(([run, result, tone], i) => {
        const y = 30 + i * 54;
        return (
          <g key={run}>
            <text className="dg-note" x={8} y={y + 26}>{run}</text>
            <Box x={186} y={y} w={246} h={40} label={result} tone={tone} />
          </g>
        );
      })}
      <text className="dg-note" x={8} y={312}>Without the two rules: 1,244 tokens in.</text>
      <text className="dg-note" x={8} y={332}>The score caught every run; reading each miss tells which kind.</text>
    </Svg>
  );
}

function L4jGuardrails() {
  // Still (owner, 26 November): chapter 25's real run; token counts from the gateway's log.
  const cols: [number, number, string][] = [[8, 130, "input guardrail"], [152, 136, "the model"], [302, 130, "output guardrail"]];
  const rows: [string, [string, BoxTone][]][] = [
    ["train question, 42 characters", [["success", "plain"], ["238 tokens in", "plain"], ["success", "plain"]]],
    ["the attack, 379 characters", [["fatal", "highlight"], ["not called: 0", "copy"], ["(skipped)", "plain"]]],
    ["the note, 111 characters", [["success", "plain"], ["255 tokens in", "plain"], ["number removed", "accent"]]],
  ];
  return (
    <Svg viewBox="0 0 440 262" label="Three real messages: the 42-character train question passes both guardrails at 238 tokens; the 379-character attack is refused by the input guardrail and the model is never called; the 111-character note passes, costs 255 tokens, and the output guardrail removes the mobile number">
      {cols.map(([x, , t]) => <text key={t} className="dg-label" x={x + 2} y={18}>{t}</text>)}
      {rows.map(([msg, cells], r) => {
        const y = 30 + r * 70;
        return (
          <g key={msg}>
            <text className="dg-note" x={10} y={y + 12}>{msg}</text>
            {cells.map(([t, tone], c) => {
              const [x, w] = cols[c];
              return (
                <g key={c}>
                  <Box x={x} y={y + 20} w={w} h={38} label={t} tone={tone} />
                  {c < 2 && <Arrow x1={x + w} y1={y + 39} x2={cols[c + 1][0]} y2={y + 39} />}
                </g>
              );
            })}
          </g>
        );
      })}
      <text className="dg-note" x={8} y={254}>A refused message never reaches the model, so it costs nothing.</text>
    </Svg>
  );
}

function L4jCapstoneGuard() {
  // Still (owner, 26 November): chapter 30's real runs; the order inside one call, the old guard against the new one.
  const left: [string, BoxTone][] = [
    ["bicycle question: 59 chars", "plain"], ["embed: 17 tokens", "plain"], ["+ rule-book pieces", "plain"],
    ["old guard: over 300", "highlight"], ["HTTP 400, no chat call", "highlight"],
  ];
  const right: [string, BoxTone][] = [
    ["guitar question: 59 chars", "plain"], ["embed the question", "plain"], ["+ luggage.txt piece", "plain"],
    ["new guard: the 59 typed", "accent"], ["answer + sources", "copy"],
  ];
  const col = (items: [string, BoxTone][], x: number) => items.map(([t, tone], i) => (
    <g key={x + "-" + i}>
      <Box x={x} y={30 + i * 62} w={206} h={44} label={t} tone={tone} />
      {i < items.length - 1 && <Arrow x1={x + 103} y1={74 + i * 62} x2={x + 103} y2={92 + i * 62} />}
    </g>
  ));
  return (
    <Svg viewBox="0 0 440 372" label="Inside one call, retrieval runs before the input guardrail. Chapter 25's guard measured the question plus the rule-book pieces, so a 59-character question about bicycles was refused with HTTP 400 after a 17-token embedding call; the capstone's guard measures only what the passenger typed, so the 59-character guitar question was answered with its source, luggage.txt">
      <text className="dg-label" x={8} y={18}>chapter 25's guard</text>
      <text className="dg-label" x={226} y={18}>the capstone's guard</text>
      {col(left, 8)}
      {col(right, 226)}
      <text className="dg-note" x={8} y={362}>Each feature passed alone; together they broke.</text>
    </Svg>
  );
}

function L4jSupervisor() {
  // Still (owner, 26 November): chapter 29's real run, all seven calls from the gateway's log (tokens in, out).
  const calls: [string, string, BoxTone][] = [
    ["planner: call the date agent", "434 in, 26 out", "accent"],
    ["date agent: asks for nextDate", "139 in, 17 out", "plain"],
    ["date agent: 2026-11-29", "170 in, 7 out", "plain"],
    ["planner: call the fare agent", "552 in, 28 out", "accent"],
    ["fare agent: asks for fare", "155 in, 16 out", "plain"],
    ["fare agent: 420", "179 in, 2 out", "plain"],
    ["planner: done, total 840", "667 in, 57 out", "copy"],
  ];
  return (
    <Svg viewBox="0 0 440 384" label="Seven real calls: the planner chooses the date agent, which asks for the nextDate tool and returns 2026-11-29; the planner chooses the fare agent, which asks for the fare tool and returns 420; the planner answers done with 840 for two adults. The planner's calls grow from 434 to 667 tokens in">
      {calls.map(([what, cost, tone], i) => {
        const y = 4 + i * 50;
        return (
          <g key={what}>
            <Box x={8} y={y} w={290} h={40} label={what} tone={tone} />
            <text className="dg-note" x={308} y={y + 25}>{cost}</text>
          </g>
        );
      })}
      <text className="dg-note" x={8} y={372}>Three planner calls decide; four calls do the work.</text>
    </Svg>
  );
}

function LcNextToken() {
  // Still (owner, 25 November): the real o200k_base tokens of Navin's answer, one pass per token.
  const toks = ["Today's", "·onion", "·rate", "·is", "·Rs", "·", "1", ",", "850", "·per", "·quint", "al", "."];
  const shown = 5;
  return (
    <Svg viewBox="0 0 440 330" label="The model writes the answer one token at a time: each pass reads everything so far, scores every possible next token, and adds the one it picks">
      <text className="dg-label" x={0} y={16}>Each pass: read all so far, score about 200,000 tokens, pick one</text>
      {toks.slice(0, shown).map((_, i) => {
        const y = 32 + i * 44;
        return (
          <g key={i}>
            <text className="dg-note" x={0} y={y + 20}>pass {i + 1}</text>
            <g className="dg-cells-small">
              <Box x={52} y={y} w={84} h={30} label="question" tone="plain" />
              {toks.slice(0, i + 1).map((t, j) => {
                const w = 14 + 8 * [...t].length;
                const x = 140 + toks.slice(0, j).reduce((sum, u) => sum + 14 + 8 * [...u].length + 4, 0);
                return <Box key={j} x={x} y={y} w={w} h={30} label={t} tone={j === i ? "highlight" : "copy"} code />;
              })}
            </g>
          </g>
        );
      })}
      <text className="dg-note" x={0} y={262}>... and so on: the whole answer is 13 tokens, so 13 passes.</text>
      <text className="dg-note" x={0} y={282}>Yellow: the token picked in that pass. "1,850" alone is 4 tokens.</text>
      <text className="dg-note" x={0} y={310} style={{ opacity: 0.8 }}>Today's onion rate is Rs 1,850 per quintal.</text>
    </Svg>
  );
}

function LcChatRequest() {
  // Still (owner, 25 November): one real request of chapter 5, there and back, with the real numbers from the
  // gateway's log (lab requests --last).
  const stops: [string, string, string, BoxTone][] = [
    ["your program (lab machine)", "POST .../chat/completions", "model ai-chat, system + user message, lab token", "plain"],
    ["LabBox gateway", "checks the token and budget", "adds max_tokens 1024, swaps in the real key", "accent"],
    ["OpenAI: gpt-4o-mini", "writes the answer", "one token at a time (chapter 4)", "plain"],
    ["back to your program", "JSON reply", "choices[0].message.content, usage: 61 in, 38 out", "copy"],
  ];
  return (
    <Svg viewBox="0 0 440 346" label="Chapter 5's request goes from the lab machine to the LabBox gateway, which calls OpenAI; the JSON answer and its usage come back">
      {stops.map(([who, what, detail, tone], i) => {
        const y = 4 + i * 86;
        return (
          <g key={who}>
            <Box x={0} y={y} w={440} h={60} label="" tone={tone} />
            <text className="dg-label" x={14} y={y + 22}>{who}: {what}</text>
            <text className="dg-note" x={14} y={y + 44}>{detail}</text>
            {i < stops.length - 1 && <Arrow x1={220} y1={y + 62} x2={220} y2={y + 84} />}
          </g>
        );
      })}
    </Svg>
  );
}

function LcAiCircles() {
  // Still (owner, 25 November): each field inside the one before, with this course's own example of each.
  const rings: [number, string, string, string][] = [
    [0, "Artificial intelligence", "any program doing something we call intelligent", "Navin's hand-written rules (this chapter)"],
    [1, "Machine learning", "the rule is learned from examples", "the 8 mm rain threshold (this chapter)"],
    [2, "Deep learning", "learning with neural networks of many layers", "spotting a sick grape leaf in a photo"],
    [3, "Generative AI", "models that create new text, images or code", "writing a reply to a farmer"],
  ];
  const inset = 22, top = 70;
  return (
    <Svg viewBox="0 0 440 420" label="Artificial intelligence contains machine learning, which contains deep learning, which contains generative AI; a large language model sits inside generative AI">
      {rings.map(([i, name, means, eg]) => {
        const x = i * inset, y = i * top, w = 440 - 2 * x, h = 418 - y - i * 12;
        return (
          <g key={name}>
            <g className={`dg-box dg-${i === 3 ? "accent" : i % 2 ? "copy" : "plain"}`}><rect x={x + 1} y={y + 1} width={w - 2} height={h - 2} rx={18} /></g>
            <text className="dg-label" x={x + 14} y={y + 22}>{name}</text>
            <text className="dg-note" x={x + 14} y={y + 40}>{means}</text>
            <text className="dg-note" x={x + 14} y={y + 58} style={{ opacity: 0.75 }}>e.g. {eg}</text>
          </g>
        );
      })}
      <Box x={90} y={300} w={260} h={44} label="a large language model (Navin's)" tone="highlight" />
      <text className="dg-note" x={220} y={364} textAnchor="middle">it sits in all four circles at once</text>
    </Svg>
  );
}

function LcTokens() {
  // The real o200k_base pieces of chapter 2's three questions (main.py); "·" marks a piece that starts with a space.
  const rows: [string, string[]][] = [
    ["English: 7 tokens", ["What", "·is", "·the", "·onion", "·rate", "·today", "?"]],
    ["Marathi, Devanagari: 8 tokens", ["आज", "·कां", "द्य", "ाचा", "·भाव", "·काय", "·आहे", "?"]],
    ["Marathi in English letters: 11 tokens", ["a", "aj", "·k", "andy", "acha", "·bh", "av", "·kay", "·aa", "he", "?"]],
  ];
  return (
    <Svg viewBox="0 0 440 262" label="The same question cut into tokens: English 7, Marathi in Devanagari 8, Marathi typed in English letters 11">
      {rows.map(([label, parts], r) => {
        let x = 0;
        const y = 8 + r * 78;
        return (
          <g key={label}>
            <text className="dg-label" x={0} y={y + 12}>{label}</text>
            <g className="dg-cells-small">
              {parts.map((p, i) => {
                const w = 12 + 8 * [...p].length;
                const el = <Box key={i} x={x} y={y + 22} w={w} h={30} label={p} tone={r === 2 ? "highlight" : "plain"} code />;
                x += w + 3;
                return el;
              })}
            </g>
          </g>
        );
      })}
      <text className="dg-note" x={0} y={252}>One box is one token. · means the piece starts with a space.</text>
    </Svg>
  );
}

function LcCosineMatrix() {
  // Real cosines from chapter 3's vectors.json (text-embedding-3-small, 256 numbers): each new question against
  // each FAQ question; the highest in each row is the one closest_question picks.
  const cols = [["office", "hours"], ["onion", "rate"], ["cold", "storage"], ["crop", "loan"], ["grape", "harvest"]];
  const rows: [string, number[]][] = [
    ["kanda bhav kay aahe aaj?", [0.112, 0.155, -0.046, 0.071, 0.006]],
    ["tomatoes cold for a week?", [0.125, 0.177, 0.425, 0.23, 0.339]],
    ["office open on Sunday?", [0.613, 0.23, 0.066, 0.024, 0.094]],
    ["money to buy seeds", [0.172, 0.17, 0.079, 0.354, 0.287]],
    ["vines sprayed, pick Friday?", [0.241, 0.15, 0.109, 0.256, 0.628]],
  ];
  const lx = 168, cw = 54, top = 46, rh = 40;
  return (
    <Svg viewBox="0 0 440 272" label="Cosine of each new question with each FAQ question; the highest in each row is the match">
      <text className="dg-note" x={0} y={18}>new question</text>
      <text className="dg-note" x={0} y={34}>(shortened)</text>
      {cols.map(([a, b], j) => (
        <g key={a}>
          <text className="dg-note" x={lx + j * cw + cw / 2} y={18} textAnchor="middle">{a}</text>
          <text className="dg-note" x={lx + j * cw + cw / 2} y={34} textAnchor="middle">{b}</text>
        </g>
      ))}
      {rows.map(([q, vals], i) => {
        const best = vals.indexOf(Math.max(...vals));
        return (
          <g key={q}>
            <text className="dg-note" x={0} y={top + i * rh + 24}>{q}</text>
            <g className="dg-cells-small">
              {vals.map((v, j) => (
                <Box key={j} x={lx + j * cw + 2} y={top + i * rh + 4} w={cw - 4} h={rh - 8} label={v.toFixed(3)} tone={j === best ? (i === 0 ? "highlight" : "copy") : "plain"} code />
              ))}
            </g>
          </g>
        );
      })}
      <text className="dg-note" x={0} y={top + 5 * rh + 18}>Green: the match. Yellow: a match, but only 0.155 against 0.112.</text>
    </Svg>
  );
}

function LcAgentLoop() {
  // Still (owner, 25 November): chapter 10's real run, as the growing list of messages, with who adds each one.
  const rows: [string, string, string, BoxTone][] = [
    ["you", "System + Human", "What is today's onion rate, and what does it|cost to store 60 crates for 10 days?", "plain"],
    ["model call 1", "AIMessage, no text, two tool calls", "mandi_price(crop=onion)|storage_cost(crates=60, days=10)", "accent"],
    ["your code", "ToolMessage x 2", "1850 (from the rate table)|1200 (60 x 10 x 2)", "copy"],
    ["model call 2", "AIMessage with text: the answer", "Today's onion rate is ₹1850 per quintal. The cost|to store 60 crates for 10 days is ₹1200.", "highlight"],
  ];
  return (
    <Svg viewBox="0 0 440 420" label="Chapter 10's agent run: the question, a model reply asking for two tools, the two tool results added by your code, and a second model reply with the answer">
      {rows.map(([who, kind, text, tone], i) => {
        const y = 4 + i * 98;
        return (
          <g key={who}>
            <Box x={0} y={y} w={440} h={78} label="" tone={tone} />
            <text className="dg-label" x={14} y={y + 22}>{who}: {kind}</text>
            {text.split("|").map((line, k) => <text key={k} className="dg-note" x={14} y={y + 44 + k * 20}>{line}</text>)}
            {i < rows.length - 1 && <Arrow x1={220} y1={y + 80} x2={220} y2={y + 96} />}
          </g>
        );
      })}
      <text className="dg-note" x={0} y={414}>No tool calls in the last reply, so the loop stops: two model calls in all.</text>
    </Svg>
  );
}

function LcMemoryThreads() {
  // Still (owner, 25 November): chapter 15's real run as two saved threads, side by side.
  const ravi: [string, string][] = [
    ["Ravi", "I am Ravi ... 40 crates."],
    ["Navin", "How many days?"],
    ["Ravi", "Cost of them for 15 days?"],
    ["Navin", "storage_cost(40, 15): 1200"],
    ["Ravi", "What is my name?"],
    ["Navin", "Your name is Ravi."],
  ];
  const asha: [string, string][] = [
    ["Asha", "Cost of them for 15 days?"],
    ["Navin", "Please tell me the number..."],
  ];
  const col = (title: string, rows: [string, string][], x: number) => (
    <g>
      <text className="dg-label" x={x} y={16}>{title}</text>
      <g className="dg-cells-small">
        {rows.map(([who, text], i) => (
          <g key={i}>
            <Box x={x} y={28 + i * 46} w={210} h={38} label="" tone={who === "Navin" ? "copy" : "plain"} />
            <text className="dg-note" x={x + 10} y={28 + i * 46 + 16} style={{ fontWeight: 600 }}>{who}</text>
            <text className="dg-note" x={x + 10} y={28 + i * 46 + 32}>{text}</text>
          </g>
        ))}
      </g>
    </g>
  );
  return (
    <Svg viewBox="0 0 440 340" label="Ravi's thread M-104 holds his whole conversation, so them means his 40 crates; Asha's thread M-221 starts empty, so Navin asks her">
      {col("thread M-104 (Ravi)", ravi, 0)}
      {col("thread M-221 (Asha)", asha, 230)}
      <text className="dg-note" x={230} y={150}>Asha's thread has no</text>
      <text className="dg-note" x={230} y={168}>Ravi in it: the same</text>
      <text className="dg-note" x={230} y={186}>words, a different answer.</text>
    </Svg>
  );
}

function LcRag() {
  // Still (owner, 25 November): chapter 19's storage question, with the real query and scores (chapters 17 and 18).
  const rows: [string, string, BoxTone][] = [
    ["once, at start", "5 rule files -> 12 chunks -> 12 vectors in the store", "plain"],
    ["the model calls search_rules", "query: \"Can I store 80 crates of onions?\"", "accent"],
    ["the store: chunks scoring 0.3 or more", "storage.txt 0.609, 0.531, 0.346, each sent with [storage.txt]", "copy"],
    ["the model answers from them", "...and names the file it used: [storage.txt]", "highlight"],
  ];
  return (
    <Svg viewBox="0 0 440 360" label="Agentic RAG for the storage question: the rule book is embedded once; the model calls search_rules with the question; the store returns the closest chunks with their sources; the model answers from them">
      {rows.map(([title, detail, tone], i) => {
        const y = 4 + i * 86;
        return (
          <g key={title}>
            <Box x={0} y={y} w={440} h={62} label="" tone={tone} />
            <text className="dg-label" x={14} y={y + 24}>{title}</text>
            <text className="dg-note" x={14} y={y + 46}>{detail}</text>
            {i < rows.length - 1 && <Arrow x1={220} y1={y + 64} x2={220} y2={y + 84} />}
          </g>
        );
      })}
      <text className="dg-note" x={0} y={354}>Only what comes back can be in the answer.</text>
    </Svg>
  );
}

function LcMcp() {
  // Still (owner, 25 November): chapter 21's real run, across two processes.
  const rows: [string, string, BoxTone][] = [
    ["MCPAdapter starts coop_server.py", "a separate process, talking MCP over its stdin and stdout (stdio)", "plain"],
    ["the server lists its tools", "mandi_price, storage_cost: they become LangChain tools", "accent"],
    ["the agent calls them over MCP", "mandi_price(grapes) and storage_cost(crates=15, days=4)", "plain"],
    ["the server runs its Python", "4600 from its rate table, 120 from 15 x 4 x 2", "copy"],
    ["the answer; then the block ends", "...grapes ₹4600 per quintal ... ₹120. The server stops.", "highlight"],
  ];
  return (
    <Svg viewBox="0 0 440 430" label="Chapter 21's run: the adapter starts the server process, lists its two tools, the agent calls them over MCP, the server computes the results, and the server stops when the block ends">
      {rows.map(([title, detail, tone], i) => {
        const y = 4 + i * 86;
        return (
          <g key={title}>
            <Box x={0} y={y} w={440} h={62} label="" tone={tone} />
            <text className="dg-label" x={14} y={y + 24}>{title}</text>
            <text className="dg-note" x={14} y={y + 46}>{detail}</text>
            {i < rows.length - 1 && <Arrow x1={220} y1={y + 64} x2={220} y2={y + 84} />}
          </g>
        );
      })}
    </Svg>
  );
}

function LcMiddleware() {
  // Still (owner, 25 November): the hooks of one agent run, with what chapter 22's middleware does at each.
  const rows: [string, string, BoxTone][] = [
    ["before_agent", "once per run: guards (chapter 24)", "plain"],
    ["before_model", "SummarizationMiddleware, ModelCallLimitMiddleware", "accent"],
    ["the model call (wrap_model_call)", "here: asks for mandi_price(onion) and (garlic)", "plain"],
    ["each tool call (wrap_tool_call)", "ToolErrorMiddleware: 1850, and garlic's error as a message", "copy"],
    ["after_agent", "once, when the model answers without tool calls", "plain"],
  ];
  return (
    <Svg viewBox="0 0 440 456" label="One agent run with middleware: before the agent, before each model call, around the model call, around each tool call, back to the model, and after the agent">
      {rows.map(([title, detail, tone], i) => {
        const y = 4 + i * 86;
        return (
          <g key={title}>
            <Box x={28} y={y} w={406} h={62} label="" tone={tone} />
            <text className="dg-label" x={42} y={y + 24}>{title}</text>
            <text className="dg-note" x={42} y={y + 46}>{detail}</text>
            {i < rows.length - 1 && <Arrow x1={231} y1={y + 64} x2={231} y2={y + 84} />}
          </g>
        );
      })}
      <path d="M28 297 C 4 297, 4 125, 26 125" className="dg-arrow" markerEnd="var(--figure-arrowhead)" />
      <text className="dg-note" x={28} y={434}>The arrow on the left: after the tools, back to</text>
      <text className="dg-note" x={28} y={452}>before_model, until the model answers.</text>
    </Svg>
  );
}

function LcWrapTool() {
  // Still (owner, 25 November): audit_tools wraps one real tool call from chapter 23's run (Ravi, 25 crates, 8 days).
  return (
    <Svg viewBox="0 0 440 400" label="audit_tools wraps the storage_cost call: it writes the audit line, calls handler, which runs the tool and gives 400, and returns that result to the model">
      <Box x={28} y={4} w={406} h={40} label="the model asks: storage_cost(crates=25, days=8)" />
      <Arrow x1={231} y1={46} x2={231} y2={70} />
      <g className="dg-box dg-accent"><rect x={28} y={72} width={406} height={216} rx={10} /></g>
      <text className="dg-label" x={42} y={96}>audit_tools(request, handler)</text>
      <text className="dg-note" x={42} y={120}>1. before: AUDIT gets</text>
      <text className="dg-note" x={56} y={140}>M-104 storage_cost {"{'crates': 25, 'days': 8}"}</text>
      <Box x={56} y={156} w={350} h={58} label="" tone="copy" />
      <text className="dg-label" x={70} y={180}>2. handler(request)</text>
      <text className="dg-note" x={70} y={202}>the tool runs: 25 x 8 x 2 = 400</text>
      <text className="dg-note" x={42} y={240}>3. after: return handler's result,</text>
      <text className="dg-note" x={42} y={260}>a ToolMessage with 400</text>
      <Arrow x1={231} y1={290} x2={231} y2={314} />
      <Box x={28} y={316} w={406} h={40} label="the model reads 400 and answers Ravi" />
      <text className="dg-note" x={28} y={380}>Skip step 2: the tool never runs. Skip the return: the run stops.</text>
    </Svg>
  );
}

function LcGuards() {
  // Still (owner, 25 November): chapter 24's two real messages through the guards (counts from the lab gateway's log).
  const lanes: [number, [string, string, BoxTone][]][] = [
    [8, [
      ["the Aadhaar question", "54 characters", "plain"],
      ["length_guard", "54 <= 500: go on", "accent"],
      ["PIIMiddleware", "4821 3390 1176 -> ****1176", "copy"],
      ["the model", "165 tokens in, 27 out", "plain"],
      ["the answer", "the full number never left", "plain"],
    ]],
    [228, [
      ["the long message", "717 characters", "plain"],
      ["length_guard", "717 > 500: refuse, end", "highlight"],
      ["PIIMiddleware", "not reached", "plain"],
      ["the model", "not reached: 0 tokens", "plain"],
      ["the answer", "TOO_LONG, from the guard", "plain"],
    ]],
  ];
  return (
    <Svg viewBox="0 0 440 448" label="Two messages through the guards: the Aadhaar question passes the length guard, is masked, and reaches the model; the 717-character message is refused by the length guard and nothing else runs">
      {lanes.map(([x, rows]) => rows.map(([title, detail, tone], i) => {
        const y = 4 + i * 84;
        return (
          <g key={`${x}-${i}`} opacity={detail.startsWith("not reached") ? 0.5 : 1}>
            <Box x={x} y={y} w={204} h={58} label="" tone={tone} />
            <text className="dg-label" x={x + 12} y={y + 23}>{title}</text>
            <text className="dg-note" x={x + 12} y={y + 44}>{detail}</text>
            {i < rows.length - 1 && <Arrow x1={x + 102} y1={y + 60} x2={x + 102} y2={y + 82} />}
          </g>
        );
      }))}
      <text className="dg-note" x={8} y={422}>before_agent hooks (length_guard) run before every</text>
      <text className="dg-note" x={8} y={440}>before_model hook (PIIMiddleware), whatever the list order.</text>
    </Svg>
  );
}

function LcLongMemory() {
  // Still (owner, 25 November): chapter 27's real run: two threads of one member, one store between them.
  return (
    <Svg viewBox="0 0 440 292" label="Thread monday saves a fact with remember into the store under M-104 facts; thread friday never sees monday's messages, but member_prompt reads the fact from the store, so the answer uses 3 acres">
      <Box x={8} y={4} w={204} h={96} label="" />
      <text className="dg-label" x={20} y={28}>thread "monday"</text>
      <text className="dg-note" x={20} y={52}>I farm 3 acres of onions</text>
      <text className="dg-note" x={20} y={72}>in Lasalgaon.</text>
      <text className="dg-note" x={20} y={92}>tool: remember</text>
      <Box x={228} y={4} w={204} h={96} label="" />
      <text className="dg-label" x={240} y={28}>thread "friday"</text>
      <text className="dg-note" x={240} y={52}>How much crop loan for</text>
      <text className="dg-note" x={240} y={72}>my whole farm?</text>
      <text className="dg-note" x={240} y={92}>Rs 1,50,000 (3 acres)</text>
      <Arrow x1={110} y1={102} x2={110} y2={166} />
      <text className="dg-note" x={118} y={140}>store.put</text>
      <Arrow x1={330} y1={168} x2={330} y2={104} />
      <text className="dg-note" x={338} y={140}>member_prompt</text>
      <text className="dg-note" x={338} y={156}>reads it</text>
      <Box x={8} y={170} w={424} h={80} label="" tone="copy" />
      <text className="dg-label" x={20} y={194}>store, namespace ("M-104", "facts")</text>
      <text className="dg-note" x={20} y={218}>key "1": Ravi Patil farms 3 acres of onions</text>
      <text className="dg-note" x={20} y={238}>in Lasalgaon.</text>
      <text className="dg-note" x={8} y={280}>The two threads share no messages, only the store.</text>
    </Svg>
  );
}

function LcHumanLoop() {
  // Still (owner, 25 November): Ravi's real booking from chapter 25's run, paused, edited by the manager, resumed.
  const rows: [string, string, BoxTone][] = [
    ["1. invoke, thread M-104", "Please book 80 crates of onions for 10 days.", "plain"],
    ["2. the model asks", "book_storage(crates=80, days=10, crop=onion)", "plain"],
    ["3. pause, before the tool runs", "__interrupt__ returned; the checkpointer keeps M-104", "highlight"],
    ["4. the manager decides", "edit: crates 50 (the rule book's 50-crate limit)", "accent"],
    ["5. invoke(Command(resume=...)), M-104", "the tool runs with 50: booking B-101", "copy"],
    ["6. the model answers", "I have booked 50 crates of onions for 10 days.", "plain"],
  ];
  return (
    <Svg viewBox="0 0 440 448" label="Ravi's booking: the model asks for 80 crates, the run pauses before the tool, the manager edits it to 50, the same thread resumes, the tool books 50 and the model says 50">
      {rows.map(([title, detail, tone], i) => {
        const y = 4 + i * 74;
        return (
          <g key={title}>
            <Box x={28} y={y} w={406} h={56} label="" tone={tone} />
            <text className="dg-label" x={42} y={y + 22}>{title}</text>
            <text className="dg-note" x={42} y={y + 43}>{detail}</text>
            {i < rows.length - 1 && <Arrow x1={231} y1={y + 58} x2={231} y2={y + 72} />}
          </g>
        );
      })}
    </Svg>
  );
}

function LgRun() {
  // Still (owner, 26 November): chapter 1's real run on "Pipe burst near the school"; updates and states as printed.
  const steps: [string, string, BoxTone][] = [
    ["START: the input", "text", "plain"],
    ["classify: {kind: leak}", "text, kind", "accent"],
    ["write_reply: {reply: ...}", "text, kind, reply", "copy"],
  ];
  return (
    <Svg viewBox="0 0 440 244" label="Pipe burst near the school: the input holds text; classify returns only kind leak and the state holds text and kind; write_reply returns only reply, promising 24 hours, and the state holds text, kind and reply">
      <text className="dg-label" x={8} y={18}>node: the update it returns</text>
      <text className="dg-label" x={262} y={18}>state afterwards</text>
      {steps.map(([update, state, tone], i) => {
        const y = 30 + i * 60;
        return (
          <g key={update}>
            <Box x={8} y={y} w={236} h={44} label={update} tone={tone} />
            <Arrow x1={244} y1={y + 22} x2={258} y2={y + 22} />
            <Box x={258} y={y} w={174} h={44} label={state} tone="plain" />
          </g>
        );
      })}
      <text className="dg-note" x={8} y={216}>The reply: "...We will respond within 24 hours."</text>
      <text className="dg-note" x={8} y={236}>Each node returns only its own keys; LangGraph merges them in.</text>
    </Svg>
  );
}

function LgReducer() {
  // Still (owner, 26 November): chapter 2's real runs on "Brown water near the district hospital."
  const rows: [string, string, string][] = [
    ["severity", "high", "urgent"],
    ["log", "last line only", "both lines"],
  ];
  return (
    <Svg viewBox="0 0 440 268" label="Brown water near the district hospital: classify sends severity urgent and one log line, check_location sends severity high and one log line. Without reducers the final severity is high and the log has only check_location's line; with the reducers severity stays urgent and the log has both lines">
      <text className="dg-label" x={8} y={18}>two updates arrive, in this order</text>
      <Box x={8} y={28} w={206} h={44} label="classify: urgent + a line" tone="plain" />
      <Box x={226} y={28} w={206} h={44} label="location: high + a line" tone="plain" />
      <text className="dg-label" x={8} y={102}>final state</text>
      <text className="dg-label" x={110} y={102}>no reducer</text>
      <text className="dg-label" x={274} y={102}>with the reducer</text>
      {rows.map(([key, plain, reduced], i) => {
        const y = 112 + i * 62;
        return (
          <g key={key}>
            <text className="dg-note" x={8} y={y + 28}>{key}</text>
            <Box x={84} y={y} w={160} h={48} label={plain} tone="highlight" />
            <Box x={252} y={y} w={180} h={48} label={reduced} tone="copy" />
          </g>
        );
      })}
      <text className="dg-note" x={8} y={248}>The first call is higher("", "urgent"): current starts empty.</text>
    </Svg>
  );
}

function LgRoute() {
  // Still (owner, 26 November): chapter 3's real run, four complaints, their tries and the node each ended at.
  const rows: [string, string, string, BoxTone][] = [
    ["Gandi Chowk", "2: after correcting", "health, North", "copy"],
    ["Station Road", "1: found at once", "repair, South", "copy"],
    ["tilaknagar", "2: after correcting", "billing office", "copy"],
    ["Shivaji Path", "2: never found", "ask_citizen", "highlight"],
  ];
  return (
    <Svg viewBox="0 0 440 300" label="Four real complaints: Gandi Chowk needed the corrected spelling and went to the health team, North zone; Station Road was found at once and went to the repair crew, South zone; tilaknagar needed the correction and went to billing; Shivaji Path was not found in two tries and went to ask_citizen">
      <text className="dg-label" x={8} y={18}>street</text>
      <text className="dg-label" x={120} y={18}>find_zone tries</text>
      <text className="dg-label" x={290} y={18}>ended at</text>
      {rows.map(([street, tries, end, tone], i) => {
        const y = 28 + i * 58;
        return (
          <g key={street}>
            <text className="dg-note" x={8} y={y + 27}>{street}</text>
            <Box x={112} y={y} w={166} h={44} label={tries} tone="plain" />
            <Arrow x1={278} y1={y + 22} x2={290} y2={y + 22} />
            <Box x={290} y={y} w={142} h={44} label={end} tone={tone} />
          </g>
        );
      })}
      <text className="dg-note" x={8} y={270}>MAX_TRIES = 2 is the way out of the loop.</text>
      <text className="dg-note" x={8} y={290}>Without it, the run stopped only at step 10,007.</text>
    </Svg>
  );
}

function LgModelNode() {
  // Still (owner, 26 November): chapter 4's real run on the Hindi complaint; tokens from the gateway's log.
  const rows: [string, string, BoxTone][] = [
    ["pani nahi aaya aaj gandhi chowk mein", "the text", "plain"],
    ["triage: the model, as Triage", "178 in, 18 out", "accent"],
    ["no_water, high, Gandhi Chowk", "checked by Literal", "plain"],
    ["Python: HOURS[\"high\"] = 24", "no model", "copy"],
    ["draft_reply: the model writes", "88 in, 29 out", "accent"],
    ["\"...within the next 24 hours.\"", "as Python set", "plain"],
  ];
  return (
    <Svg viewBox="0 0 440 372" label="The Hindi complaint: triage asks the model for a Triage object, 178 tokens in and 18 out, and gets no_water, high, Gandhi Chowk; Python looks up 24 hours; draft_reply asks the model to write the reply, 88 tokens in and 29 out, and it promises within the next 24 hours">
      {rows.map(([what, note, tone], i) => {
        const y = 4 + i * 60;
        return (
          <g key={what}>
            <Box x={8} y={y} w={290} h={44} label={what} tone={tone} />
            <text className="dg-note" x={308} y={y + 27}>{note}</text>
            {i < rows.length - 1 && <Arrow x1={153} y1={y + 44} x2={153} y2={y + 60} />}
          </g>
        );
      })}
    </Svg>
  );
}

function LgJoin() {
  // Still (owner, 26 November): chapter 5's real Station Road run, plus the measured join facts.
  return (
    <Svg viewBox="0 0 440 300" label="Station Road: in step 1 zone_lookup returns South and history_lookup returns 6 past complaints, at the same time; in step 2 assign runs once and plans the South zone crew and a survey of the old main. Measured: two one-second nodes in one step took 1.00 seconds; with uneven branches separate edges ran assign twice, the list join once">
      <text className="dg-label" x={8} y={18}>step 1: both at once</text>
      <Box x={8} y={28} w={206} h={44} label="zone_lookup: South" tone="accent" />
      <Box x={226} y={28} w={206} h={44} label="history_lookup: 6 past" tone="accent" />
      <Arrow x1={111} y1={72} x2={200} y2={104} />
      <Arrow x1={329} y1={72} x2={240} y2={104} />
      <text className="dg-label" x={8} y={98}>step 2: the join</text>
      <Box x={8} y={106} w={424} h={44} label="assign, once: South crew + survey of the main" tone="copy" />
      <text className="dg-label" x={8} y={180}>measured</text>
      <text className="dg-note" x={8} y={202}>Two 1-second nodes in one step: 1.00 s, not 2.</text>
      <text className="dg-note" x={8} y={224}>Uneven branches, separate edges: assign ran 2 times.</text>
      <text className="dg-note" x={8} y={246}>Uneven branches, add_edge([a, b], assign): 1 time.</text>
      <text className="dg-note" x={8} y={268}>Both writing one key, no reducer: InvalidUpdateError.</text>
    </Svg>
  );
}

function LgSend() {
  // Still (owner, 26 November): chapter 6's real storm night, five Sends and four Commands.
  const repairs: [string, string, BoxTone][] = [
    ["leak, Rs 18,000", "tomorrow", "plain"],
    ["no_water, Rs 65,000", "engineer_approval", "accent"],
    ["urgent dirty_water, Rs 40,000", "tomorrow!", "highlight"],
    ["leak, Rs 18,000", "tomorrow", "plain"],
  ];
  return (
    <Svg viewBox="0 0 440 368" label="Five complaints become five Sends to triage_one, all in one step; operator.add collects five tickets and summarise reports 5 complaints, 1 urgent. Then a Command per repair: the Rs 65,000 no_water repair goes to the engineer, the others to tomorrow's schedule, including the urgent brown water, because plan only reads the cost">
      <text className="dg-label" x={8} y={18}>one step: a Send per complaint to triage_one</text>
      {[0, 1, 2, 3, 4].map((i) => <Box key={i} x={8 + i * 86} y={28} w={78} h={36} label="triage" tone="accent" />)}
      <Arrow x1={220} y1={64} x2={220} y2={80} />
      <Box x={8} y={80} w={424} h={40} label="5 tickets joined: 5 complaints, 1 urgent" tone="copy" />
      <text className="dg-label" x={8} y={152}>then plan returns a Command per repair: engineer or schedule</text>
      {repairs.map(([what, where, tone], i) => {
        const y = 162 + i * 46;
        return (
          <g key={i}>
            <Box x={8} y={y} w={236} h={36} label={what} tone="plain" />
            <Arrow x1={244} y1={y + 18} x2={258} y2={y + 18} />
            <Box x={258} y={y} w={174} h={36} label={where} tone={tone} />
          </g>
        );
      })}
      <text className="dg-note" x={8} y={360}>plan reads only the cost: the urgent repair waits a day.</text>
    </Svg>
  );
}

function LgThreads() {
  // Still (owner, 26 November): chapter 7's real run, three processes sharing harsh.db.
  const runs: [string, string, string, BoxTone][] = [
    ["process 1, phone 98220", "loads: empty", "saves: 2 messages", "plain"],
    ["process 2, phone 98220", "loads: 2 messages", "saves: 4 messages", "copy"],
    ["process 3, phone 70300", "loads: empty", "saves: 2 messages", "plain"],
  ];
  return (
    <Svg viewBox="0 0 440 270" label="Three separate processes share the file harsh.db: the first message from 98220 loads an empty thread and saves 2 messages; the second process for 98220 loads those 2 and saves 4; phone 70300 loads an empty thread of its own and saves 2">
      <text className="dg-label" x={8} y={18}>each run: load the thread, run, save</text>
      {runs.map(([who, load, save, tone], i) => {
        const y = 30 + i * 62;
        return (
          <g key={who}>
            <text className="dg-note" x={8} y={y + 14}>{who}</text>
            <Box x={8} y={y + 20} w={200} h={34} label={load} tone="plain" />
            <Arrow x1={208} y1={y + 37} x2={224} y2={y + 37} />
            <Box x={224} y={y + 20} w={208} h={34} label={save} tone={tone} />
          </g>
        );
      })}
      <Box x={8} y={222} w={424} h={36} label="harsh.db: every checkpoint of every thread" tone="accent" />
    </Svg>
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

function RsMonomorph() {
  return (
    <SketchSteps
      title="One generic function, three real ones"
      intro="Press Play to follow largest through the compiler."
      label="Generics"
      steps={[
        { label: "the source", says: "largest<T: PartialOrd + Copy> is written once." },
        { label: "checked once", says: "The compiler checks the body against the bounds: > needs PartialOrd, copying needs Copy." },
        { label: "used with f64", says: "A call with power readings makes a copy of largest for f64." },
        { label: "used with u16 and char", says: "Fault codes and hour letters make two more copies, each for its own type." },
        { label: "optimised", says: "Each copy is optimised like code written for that type by hand: no checks at run time." },
      ]}
    />
  );
}

function RsTraitObject() {
  return (
    <SketchSteps
      title="One report, different sensors"
      intro="Press Play to follow report() through a Vec<Box<dyn Sensor>>."
      label="Trait objects"
      steps={[
        { label: "the Vec", says: "Three boxes. Each holds a sensor's data and a pointer to its type's Sensor methods (a vtable)." },
        { label: "T07 anemometer", says: "describe() asks the vtable for Anemometer's id, value and unit: 12.4 m/s." },
        { label: "T07 power meter", says: "The next box points at PowerMeter's methods: 2100.0 kW." },
        { label: "the default", says: "describe() itself was written once, in the trait, for every sensor." },
        { label: "next year", says: "A new sensor type is one new impl Sensor; report() does not change." },
      ]}
    />
  );
}

function RsLifetime() {
  return (
    <SketchSteps
      title="A LogLine and its line"
      intro="Press Play to see why the LogLine may not outlive the line."
      label="Lifetimes"
      steps={[
        { label: "the line", says: 'A String holds "T07,2026-11-24 10:10,12.4,2100" on the heap.' },
        { label: "LogLine::parse", says: "Four &str fields point into that String: nothing is copied." },
        { label: "'a", says: "LogLine<'a> says: these fields are valid only while the line is." },
        { label: "the line is dropped", says: "At the end of its block the String frees its memory." },
        { label: "refused", says: "Using the LogLine after that would read freed memory, so E0597 stops the build." },
      ]}
    />
  );
}

function RsClosure() {
  return (
    <SketchSteps
      title="Rules as values"
      intro="Press Play to follow T19 through three rules."
      label="Closures"
      steps={[
        { label: "below(200.0)", says: "Returns a closure that owns its own copy of 200.0 (move)." },
        { label: "the list", says: "Three rules, each a different closure, boxed so they share one type." },
        { label: "low power", says: "T19: wind 26 >= 6 and power 0 < 200: true. A false alarm: T19 is stopped for a storm." },
        { label: "storm stop", says: "The closure captured storm_limit, 25.0: 26 >= 25, true." },
        { label: "idle in good wind", says: "Wind 26 >= 6 and power 0: true again. Each rule is right alone and wrong together." },
      ]}
    />
  );
}

function RsIteratorChain() {
  return (
    <SketchSteps
      title="Items through a chain"
      intro="Press Play to follow three readings through filter, filter, map, collect."
      label="Iterators"
      steps={[
        { label: "collect asks", says: "Nothing has happened yet. collect asks the chain for its first item." },
        { label: "T07, 12.4 m/s, 2100 kW", says: "Strong wind: kept. Power 2100 is not below 2000: dropped. No list was made." },
        { label: "T12, 13.0 m/s, 1450 kW", says: 'Strong wind: kept. 1450 < 2000: kept. map gives "T12"; collect stores it.' },
        { label: "T31, 26.0 m/s", says: "26 is a storm: dropped by the first filter." },
        { label: "done", says: 'The chain runs out; collect returns ["T12"]. In release, all of this is one loop.' },
      ]}
    />
  );
}

function RsTestMutation() {
  return (
    <SketchSteps
      title="How your tests are judged"
      intro="Press Play to follow power_curve_edges through the check."
      label="Tests"
      steps={[
        { label: "correct code", says: "Your test runs on the reference library: every assert must hold." },
        { label: "plant a bug", says: "The check changes one thing: wind_ms >= 25.0 becomes wind_ms > 25.0." },
        { label: "run again", says: "At exactly 25 m/s the curve now says 2500 kW instead of 0." },
        { label: "caught", says: "If your test asserts power_curve(25.0) == 0.0, it fails: the task passes." },
        { label: "not caught", says: "A test that never looks at 25 m/s still passes: the check says it is too weak." },
      ]}
    />
  );
}

function RsCli() {
  return (
    <SketchSteps
      title="A command line becomes a struct"
      intro="Press Play to follow one command line through clap."
      label="clap"
      steps={[
        { label: "the words", says: "The shell hands Windwatch four words: data/farm.csv --turbine T12 --low-kw 300." },
        { label: "positional", says: "data/farm.csv has no -- in front, so it fills the first positional field, file." },
        { label: "--turbine T12", says: 'A long option: clap finds the field named turbine and stores Some("T12").' },
        { label: "--low-kw 300", says: "low_kw becomes --low-kw. The text 300 is converted to the f64 300.0." },
        { label: "left out", says: "Had --low-kw been missing, the default 200.0 would fill it, as --help says." },
        { label: "a mistake", says: "--turbin matches no field: clap prints an error with a suggestion and exits before run() starts." },
      ]}
    />
  );
}

function RsRcRefCell() {
  return (
    <SketchSteps
      title="One crew, three owners"
      intro="Press Play to follow the North crew through Rc and RefCell."
      label="Rc and RefCell"
      steps={[
        { label: "Rc::new", says: "The North crew is made inside a RefCell inside an Rc. Count: 1 (north, in main)." },
        { label: "Rc::clone twice", says: "T12 and T19 each get a pointer to the same crew. Count: 3. No crew was copied." },
        { label: "T12 reports", says: "borrow_mut() marks the crew as borrowed, the job is pushed, and the borrow ends at the semicolon." },
        { label: "T19 reports", says: "Nothing else is borrowing, so its borrow_mut() succeeds too: two jobs in one list." },
        { label: "drop(t19)", says: "T19's pointer is gone. Count: 2. The crew stays, because others still hold it." },
        { label: "the last owner", says: "When the count reaches 0, the crew and its jobs are dropped." },
      ]}
    />
  );
}

function RsThreads() {
  return (
    <SketchSteps
      title="Forty logs on every CPU"
      intro="Press Play to follow parallel_totals through a scope."
      label="Threads"
      steps={[
        { label: "thread::scope", says: "A scope opens. Every thread started inside must finish before it closes." },
        { label: "spawn x 40", says: "One thread per log starts at once. Each borrows its log; nothing is copied." },
        { label: "running", says: "The operating system runs them on every CPU it has; with 2 CPUs, two at a time." },
        { label: "join in order", says: "join() waits for T01's thread, then T02's, and so on; the sums come back in the logs' order." },
        { label: "the scope closes", says: "All threads are finished, so the borrows of logs end safely." },
        { label: "Rc refused", says: "A thread given an Rc does not compile: Rc is not Send (E0277)." },
      ]}
    />
  );
}

function RsAsync() {
  return (
    <SketchSteps
      title="Forty polls on one thread"
      intro="Press Play to follow poll_all through the runtime."
      label="Async"
      steps={[
        { label: "spawn x 39", says: "Each poll becomes a task in the JoinSet. Spawning does not wait." },
        { label: "first await", says: "T01's task sends its request and reaches sleep(...).await: it is parked, and the thread moves on." },
        { label: "all parked", says: "In a few microseconds every task is waiting. The thread has nothing to do and sleeps." },
        { label: "woken", says: "After 100 to 142 ms the timers fire one by one; each task is woken and finishes its answer." },
        { label: "join_next", says: "Answers arrive in the order they finish; at the end they are sorted by id." },
        { label: "timeout", says: "T31 is given 500 ms. When the time is up, its future is dropped where it waited." },
      ]}
    />
  );
}

function RsSpeed() {
  return (
    <SketchSteps
      title="Half a million lines, no copies"
      intro="Press Play to follow two lines into the map."
      label="Borrowing"
      steps={[
        { label: "the text", says: "read_to_string gives one String of 16 MB: every line of the quarter." },
        { label: "lines()", says: "Each line is a slice of that String: a start and a length." },
        { label: "split_once", says: '"T07" is a slice of the line, so a slice of the text. The power is parsed into an f64.' },
        { label: 'entry("T07")', says: "The map's key is that slice. The first T07 line adds the key; no String is made." },
        { label: "the next T07", says: "Later T07 lines find the same key and add to its total." },
        { label: "the result", says: "40 keys, all pointing into the text. The map may not outlive the text, and the compiler checks it." },
      ]}
    />
  );
}

function RsCapstone() {
  return (
    <SketchSteps
      title="Two requests through Windwatch"
      intro="Press Play to follow a POST and a GET."
      label="axum"
      steps={[
        { label: "POST /readings", says: "A turbine sends JSON. The router matches the method and the path to add_reading." },
        { label: "Json extractor", says: "serde turns the body into a Reading. A missing field is answered with 422 here." },
        { label: "your rule", says: "power_kw 9999 is impossible: 422. 140 is fine: lock the store, push, answer 201." },
        { label: "GET /turbines/T12/summary", says: "The Path extractor takes T12 from the path; summary locks the same store." },
        { label: "the summary", says: "2 readings, average 222.5 kW, 2 below 80% of the curve: sent back as JSON with 200." },
        { label: "T99", says: "No readings: ok_or gives Err(NOT_FOUND), and the question mark sends the 404." },
      ]}
    />
  );
}

/** RAG in one picture, with the chapter's real question, the sections keyword search really found and the real answer. */
function RagFlow() {
  const t = { fontSize: 13.5 };
  return (
    <Svg viewBox="0 0 440 446" label="A question goes to the search, the sections found go into the prompt with the question, and the model answers from them, naming the section">
      <text className="dg-note" x={0} y={14}>1. the ranger's question</text>
      <g className="dg-box dg-accent">
        <rect x={0} y={22} width={440} height={54} rx={8} />
        <text x={220} y={44} textAnchor="middle" style={t}>How often should we change the batteries</text>
        <text x={220} y={64} textAnchor="middle" style={t}>in the camera traps?</text>
      </g>
      <Arrow x1={30} y1={78} x2={30} y2={110} />
      <text className="dg-note" x={42} y={99}>2. retrieve: search the manual</text>
      <Box x={0} y={114} w={120} h={34} label="FM-3.2" tone="highlight" code />
      <Box x={128} y={114} w={120} h={34} label="FM-3.1" code />
      <Box x={256} y={114} w={120} h={34} label="FM-7.1" code />
      <Arrow x1={30} y1={150} x2={30} y2={182} />
      <text className="dg-note" x={42} y={171}>3. augment: sections + question in one prompt</text>
      <g className="dg-box dg-plain">
        <rect x={0} y={186} width={440} height={118} rx={8} />
        <text className="dg-code" x={12} y={208} style={{ fontSize: 12, fontWeight: 400 }}>Manual sections:</text>
        <text className="dg-code" x={12} y={230} style={{ fontSize: 12, fontWeight: 400 }}>[FM-3.2] Batteries and memory cards</text>
        <text className="dg-code" x={12} y={248} style={{ fontSize: 12, fontWeight: 400 }}>Change the batteries ... every 21 days ...</text>
        <text className="dg-code" x={12} y={270} style={{ fontSize: 12, fontWeight: 400 }}>[FM-3.1] Camera traps ...</text>
        <text className="dg-code" x={12} y={292} style={{ fontSize: 12, fontWeight: 400 }}>Question: How often should we change ...</text>
      </g>
      <Arrow x1={30} y1={306} x2={30} y2={338} />
      <text className="dg-note" x={42} y={327}>4. generate: the model reads the prompt</text>
      <g className="dg-box dg-highlight">
        <rect x={0} y={342} width={440} height={56} rx={8} />
        <text x={220} y={365} textAnchor="middle" style={t}>You should change the batteries of every camera</text>
        <text x={220} y={385} textAnchor="middle" style={t}>trap every 21 days. [FM-3.2]</text>
      </g>
      <text className="dg-note" x={0} y={420}>The answer names its section, so anyone can open FM-3.2</text>
      <text className="dg-note" x={0} y={438}>and check it.</text>
    </Svg>
  );
}

function RagEmbed() {
  const rows = [
    { text: "A tiger crossed the path.", nums: ["-0.019", "-0.013", "0.011", "0.056"], tone: "accent" as BoxTone },
    { text: "A big cat walked across the trail.", nums: ["-0.021", "-0.058", "-0.003", "0.080"], tone: "accent" as BoxTone },
    { text: "Change the camera trap batteries every 21 days.", nums: ["-0.068", "-0.003", "0.001", "0.003"], tone: "plain" as BoxTone },
  ];
  const t = { fontSize: 13.5 };
  return (
    <Svg viewBox="0 0 440 470" label="Each sentence goes through the embedding model and comes out as a row of 384 numbers; tiger and big cat score 0.69, tiger and batteries 0.42">
      {rows.map((r, n) => {
        const y = n * 124;
        return (
          <g key={r.text}>
            <g className={`dg-box dg-${r.tone}`}>
              <rect x={0} y={y} width={440} height={36} rx={8} />
              <text x={220} y={y + 23} textAnchor="middle" style={t}>{r.text}</text>
            </g>
            <Arrow x1={40} y1={y + 38} x2={40} y2={y + 70} />
            <text className="dg-note" x={52} y={y + 59}>the bge-small model</text>
            <g className="dg-cells-small">
              {r.nums.map((v, k) => <Box key={k} x={k * 64} y={y + 74} w={60} h={34} label={v} tone={r.tone} code />)}
            </g>
            <text className="dg-note" x={262} y={y + 96}>... 380 more numbers</text>
          </g>
        );
      })}
      <text className="dg-note" x={0} y={392}>compare two vectors with cosine similarity:</text>
      <Box x={0} y={402} w={440} h={30} label="tiger vs big cat: 0.69, close" tone="highlight" />
      <Box x={0} y={438} w={440} h={30} label="tiger vs batteries: 0.42, far" />
    </Svg>
  );
}

/** Brute-force search: the section matrix times the question's vector gives one score per section; the top 3 win.
 *  Real cosines for "What should I do if a big cat is right in front of me?" (bge-small, chapter 3). */
function RagMatrix() {
  const rows = [["FM-1.1", "0.411"], ["FM-2.2", "0.436"], ["FM-4.1", "0.551"], ["FM-4.2", "0.595"], ["FM-7.3", "0.565"]];
  const best = new Set(["FM-4.2", "FM-7.3", "FM-4.1"]);
  return (
    <Svg viewBox="0 0 440 420" label="The matrix of 31 section vectors times the question vector gives 31 scores; the three highest are FM-4.2, FM-7.3 and FM-4.1">
      <text className="dg-note" x={0} y={14}>the matrix: one row per section</text>
      <text className="dg-note" x={0} y={30}>(31 rows; 5 shown)</text>
      {rows.map(([id], i) => <Box key={id} x={0} y={42 + i * 40} w={150} h={34} label={`${id}  [ ... ]`} tone={best.has(id) ? "accent" : "plain"} code />)}
      <text className="dg-note" x={0} y={256}>... 26 more rows</text>
      <text x={172} y={150} className="dg-note" style={{ fontSize: 22 }}>@</text>
      <text className="dg-note" x={200} y={14}>the question</text>
      <text className="dg-note" x={200} y={30}>(384 numbers)</text>
      <g className="dg-box dg-highlight"><rect x={200} y={42} width={58} height={194} rx={8} />
        <text x={229} y={132} textAnchor="middle" className="dg-code" style={{ fontSize: 12 }}>big</text>
        <text x={229} y={148} textAnchor="middle" className="dg-code" style={{ fontSize: 12 }}>cat</text></g>
      <text x={272} y={150} className="dg-note" style={{ fontSize: 22 }}>=</text>
      <text className="dg-note" x={300} y={14}>one score per row</text>
      <text className="dg-note" x={300} y={30}>(31 cosines)</text>
      {rows.map(([id, sc], i) => <Box key={id} x={300} y={42 + i * 40} w={100} h={34} label={sc} tone={best.has(id) ? "accent" : "plain"} code />)}
      <Arrow x1={30} y1={268} x2={30} y2={296} />
      <text className="dg-note" x={42} y={287}>keep the 3 highest scores (top_k)</text>
      <Box x={0} y={302} w={440} h={34} label="1.  FM-4.2 Meeting a tiger   0.595" tone="highlight" />
      <Box x={0} y={342} w={440} h={34} label="2.  FM-7.3 Finding a dead animal   0.565" />
      <Box x={0} y={382} w={440} h={34} label="3.  FM-4.1 General rules for animal encounters   0.551" />
    </Svg>
  );
}

/** Three ways of cutting three real sections (FM-4.1 59 words, FM-4.2 66, FM-4.3 66), drawn to scale, with each
 *  method's real hit@1 from chapter 4's comparison over the whole manual. */
function RagChunks() {
  const W = 440 / 191;                           // pixels per word: the three sections are 191 words
  const secs = [["FM-4.1", 59], ["FM-4.2", 66], ["FM-4.3", 66]] as const;
  const starts = [0, 59, 125];
  const bar = (x: number, w: number, y: number, tone: string, key: string | number, label?: string) => (
    <g key={key} className={`dg-box dg-${tone}`}>
      <rect x={x} y={y} width={Math.max(2, w - 2)} height={26} rx={4} />
      {label ? <text x={x + w / 2} y={y + 18} textAnchor="middle" style={{ fontSize: 12.5 }}>{label}</text> : null}
    </g>
  );
  const borders = starts.slice(1).map((st) => st * W);
  const row = (y: number, title: string, hit: string) => (
    <><text className="dg-note" x={0} y={y - 6}>{title}</text><text className="dg-note" x={440} y={y - 6} textAnchor="end">hit@1 {hit}</text></>
  );
  return (
    <Svg viewBox="0 0 440 352" label="Three sections cut four ways: 15-word windows, 60-word windows with overlap, 300-word windows, and one chunk per section; one chunk per section, title first, finds the right section first most often">
      <text className="dg-note" x={0} y={14}>three sections of the manual, to scale (191 words)</text>
      {secs.map(([id, n], i) => bar(starts[i] * W, n * W, 22, "accent", id, `${id}  (${n} words)`))}
      {row(80, "windows of 15 words (cross the section borders)", "73%")}
      {Array.from({ length: 13 }, (_, i) => bar(i * 15 * W, Math.min(15, 191 - i * 15) * W, 80, "plain", "a" + i))}
      {row(138, "windows of 60 words, 10 overlapping", "77%")}
      {[0, 50, 100, 150].map((st, i) => bar(st * W, Math.min(60, 191 - st) * W, 138 + (i % 2) * 14, "plain", "b" + i))}
      {row(212, "windows of 300 words: one window holds all three and more", "77%")}
      {bar(0, 440, 212, "plain", "c", "one blurry chunk about many things")}
      {row(270, "one chunk per section, title first", "91%")}
      {secs.map(([id, n], i) => bar(starts[i] * W, n * W, 270, "highlight", "d" + id, `${id}. title + text`))}
      {borders.map((x) => <line key={x} x1={x} y1={20} x2={x} y2={300} className="dg-arrow" style={{ strokeDasharray: "3 4", markerEnd: "none" }} />)}
      <text className="dg-note" x={0} y={326}>Dashed lines: where one section ends and the next begins.</text>
      <text className="dg-note" x={0} y={344}>hit@1: how often the best chunk holds the right section (22 questions).</text>
    </Svg>
  );
}

/** IVF as a sketch in two dimensions (real vectors have 384): cells around centroids, the question, the probed cell,
 *  and a true neighbour just across a border. Below, the real recall from chapter 5's benchmark (100,000 synthetic
 *  vectors, 316 lists). */
function RagIvf() {
  const cells = [[0, 0], [1, 0], [2, 0], [0, 1], [1, 1], [2, 1]];
  const cw = 146, ch = 104;
  const pts = [[30, 30], [60, 70], [100, 40], [180, 25], [220, 80], [260, 50], [330, 30], [390, 75], [350, 60],
               [40, 150], [90, 185], [120, 140], [175, 135], [205, 190], [250, 165], [320, 180], [400, 140], [360, 195]];
  return (
    <Svg viewBox="0 0 440 360" label="Six cells, each around a centroid; the question sits in the middle cell near its left border; nprobe 1 searches only that cell and misses a true neighbour just across the border">
      {cells.map(([cx, cy]) => {
        const on = cx === 1 && cy === 1;
        return (
          <g key={`${cx}${cy}`} className={`dg-box dg-${on ? "highlight" : "plain"}`}>
            <rect x={cx * cw + 2} y={cy * ch + 2} width={cw - 4} height={ch - 4} rx={6} />
            <text x={cx * cw + cw / 2} y={cy * ch + ch / 2 + 5} textAnchor="middle" style={{ fontSize: 20 }}>+</text>
          </g>
        );
      })}
      {pts.map(([x, y], k) => <circle key={k} cx={x} cy={y} r={3.5} className="dg-arrow" style={{ fill: "var(--figure-text)", stroke: "none" }} />)}
      <circle cx={162} cy={160} r={7} style={{ fill: "var(--vermilion, #c63f28)" }} />
      <text className="dg-note" x={162} y={226} textAnchor="middle">question</text>
      <circle cx={134} cy={164} r={5.5} style={{ fill: "none", stroke: "var(--vermilion, #c63f28)", strokeWidth: 2.5 }} />
      <text className="dg-note" x={70} y={226} textAnchor="middle">true neighbour</text>
      <text className="dg-note" x={70} y={240} textAnchor="middle">missed: other cell</text>
      <text className="dg-note" x={0} y={262}>+ a centroid; each cell holds the vectors nearest to it.</text>
      <text className="dg-note" x={0} y={280}>nprobe 1: search only the question's cell (yellow).</text>
      <text className="dg-note" x={0} y={306}>Real recall at nprobe 1, 4, 16, 64 (100,000 synthetic vectors):</text>
      <Box x={0} y={314} w={104} h={34} label="nprobe 1: 52%" code />
      <Box x={112} y={314} w={104} h={34} label="4: 74%" code />
      <Box x={224} y={314} w={104} h={34} label="16: 92%" tone="highlight" code />
      <Box x={336} y={314} w={104} h={34} label="64: 99.6%" code />
    </Svg>
  );
}

/** HNSW as a still picture: three layers of the same graph, a search entering at the top and walking down to the
 *  question's nearest neighbour. Below, the real result from chapter 6's benchmark (100,000 synthetic vectors). */
function RagHnsw() {
  const L = [
    { y: 40, name: "layer 2: few nodes, long links", xs: [40, 230, 400] },
    { y: 140, name: "layer 1: more nodes, shorter links", xs: [40, 100, 170, 230, 300, 360, 400] },
    { y: 240, name: "layer 0: every vector, short links", xs: [20, 50, 80, 110, 140, 170, 200, 230, 260, 290, 320, 350, 380, 410] },
  ];
  const path = [[40, 40], [230, 40], [230, 140], [300, 140], [300, 240], [320, 240]];
  const node = (x: number, y: number, on: boolean, k: string) => (
    <circle key={k} cx={x} cy={y} r={on ? 7 : 5} style={{ fill: on ? "var(--vermilion, #c63f28)" : "var(--figure-text)", opacity: on ? 1 : 0.55 }} />
  );
  const onPath = (x: number, y: number) => path.some(([px, py]) => px === x && py === y);
  return (
    <Svg viewBox="0 0 440 372" label="Three layers of an HNSW graph; the search enters at the top, hops along long links, drops down a layer at a time, and ends next to the question on the bottom layer">
      {L.map((l) => (
        <g key={l.y}>
          <text className="dg-note" x={0} y={l.y - 18}>{l.name}</text>
          {l.xs.slice(0, -1).map((x, k) => <line key={k} x1={x} y1={l.y} x2={l.xs[k + 1]} y2={l.y} className="dg-arrow" style={{ markerEnd: "none", opacity: 0.35 }} />)}
          {l.xs.map((x) => node(x, l.y, onPath(x, l.y), `${l.y}-${x}`))}
        </g>
      ))}
      {path.slice(0, -1).map(([x1, y1], k) => {
        const [x2, y2] = path[k + 1];
        return <Arrow key={k} x1={x1 + (x2 > x1 ? 8 : 0)} y1={y1 + (y2 > y1 ? 8 : 0)} x2={x2 - (x2 > x1 ? 9 : 0)} y2={y2 - (y2 > y1 ? 9 : 0)} />;
      })}
      <text className="dg-note" x={40} y={64} textAnchor="middle">entry</text>
      <circle cx={334} cy={262} r={6} style={{ fill: "none", stroke: "var(--vermilion, #c63f28)", strokeWidth: 2.5 }} />
      <text className="dg-note" x={334} y={284} textAnchor="middle">question</text>
      <text className="dg-note" x={0} y={312}>Each hop moves to the linked node closest to the question.</text>
      <text className="dg-note" x={0} y={332}>Real result, 100,000 synthetic vectors, efSearch 64:</text>
      <Box x={0} y={340} w={440} h={30} label="recall 98.9%, 0.19 ms a question (brute force: 6.57 ms)" tone="highlight" />
    </Svg>
  );
}

function RagBinary() {
  // Real rows from quant_bench.py's first question (100,000 synthetic vectors); true = in the exact top 10.
  const byBits: [string, number, boolean][] = [
    ["58473", 62, true], ["765", 69, true], ["57496", 71, true], ["65850", 71, true], ["34650", 72, true], ["7959", 74, false],
    ["84978", 74, true], ["4353", 75, false], ["39354", 76, true], ["7186", 77, false], ["28950", 77, true], ["47390", 77, false],
    ["47778", 77, true], ["63714", 77, false], ["14751", 78, false], ["95241", 78, true],
  ];
  const exact: [string, string][] = [
    ["57496", "0.844"], ["58473", "0.836"], ["95241", "0.824"], ["65850", "0.810"], ["28950", "0.802"],
    ["47778", "0.797"], ["765", "0.788"], ["39354", "0.783"], ["34650", "0.782"], ["84978", "0.780"],
  ];
  const top = 60, step = 21, h = 18, w = 170, rx = 270;
  const yOf = (i: number) => top + i * step;
  return (
    <Svg viewBox="0 0 440 478" label="One question's 16 closest rows by bits, with the true top 10 marked, joined to the exact top 10 after rescoring with the full vectors">
      <text className="dg-label" x={0} y={18}>Bits: rough order</text>
      <text className="dg-note" x={0} y={38}>row: differing bits</text>
      <text className="dg-label" x={rx} y={18}>Floats: exact order</text>
      <text className="dg-note" x={rx} y={38}>row: exact score</text>
      {byBits.map(([row, , t], i) => {
        const j = exact.findIndex(([r]) => r === row);
        return j < 0 ? null : (
          <line key={`l${row}`} className="dg-arrow" x1={w} y1={yOf(i) + h / 2} x2={rx} y2={yOf(j) + h / 2} style={{ opacity: t ? 0.55 : 0 }} />
        );
      })}
      <g className="dg-cells-small">
        {byBits.map(([row, d, t], i) => (
          <Box key={`b${row}`} x={0} y={yOf(i)} w={w} h={h} label={`${row}: ${d} bits`} tone={t ? "copy" : "plain"} code />
        ))}
        {exact.map(([row, sc], j) => (
          <Box key={`e${row}`} x={rx} y={yOf(j)} w={w} h={h} label={`${row}: ${sc}`} tone="copy" code />
        ))}
      </g>
      <text className="dg-note" x={rx} y={yOf(10) + 16}>the 10 nearest, best first</text>
      <text className="dg-note" x={0} y={410}>Green: the 10 true nearest. Bits alone keep 7 of them.</text>
      <text className="dg-note" x={0} y={430}>Real recall over 100 questions (shortlist size: recall):</text>
      {[["10", "57.2%"], ["50", "93.7%"], ["200", "99.8%"]].map(([n, rc], i) => (
        <Box key={n} x={i * 150} y={442} w={140} h={32} label={`${n}: ${rc}`} tone="highlight" />
      ))}
    </Svg>
  );
}

function RagFilter() {
  // Real results from store.py: "a leopard near people", wanted: reports from the buffer zone, k = 3.
  const after: [string, string, boolean][] = [
    ["FM-4.3  manual  0.739", "dropped: not a report", false],
    ["R-0410  buffer  0.686", "kept", true],
    ["R-0407  tourism  0.664", "dropped: tourism zone", false],
  ];
  const inside: [string, string][] = [
    ["R-0410  buffer  0.686", "leopard in Rajur"],
    ["R-0302  buffer  0.650", "leopard took a goat"],
    ["R-0307  buffer  0.554", "gaur herd: weaker"],
  ];
  const row = (y: number, label: string, kept: boolean, note: string, k: string) => (
    <g key={k} style={{ opacity: kept ? 1 : 0.5 }}>
      <Box x={0} y={y} w={250} h={28} label={label} tone={kept ? "copy" : "plain"} code />
      {!kept && <line x1={12} y1={y + 14} x2={238} y2={y + 14} className="dg-arrow" style={{ markerEnd: "none" }} />}
      <text className="dg-note" x={262} y={y + 19}>{note}</text>
    </g>
  );
  return (
    <Svg viewBox="0 0 440 400" label="Filtering after the search leaves one result; filtering inside the search returns three">
      <text className="dg-note" x={0} y={16}>Question: a leopard near people. Wanted: reports from the</text>
      <text className="dg-note" x={0} y={34}>buffer zone, k = 3. Real scores from store.py.</text>
      <text className="dg-label" x={0} y={68}>Filter after: take the top 3, then drop</text>
      <g className="dg-cells-small">{after.map(([l, n, k], i) => row(80 + i * 34, l, k, n, `a${i}`))}</g>
      <Box x={0} y={186} w={250} h={28} label="1 result" tone="highlight" />
      <text className="dg-label" x={0} y={250}>Filter inside the search</text>
      <g className="dg-cells-small">{inside.map(([l, n], i) => row(262 + i * 34, l, true, n, `i${i}`))}</g>
      <Box x={0} y={368} w={250} h={28} label="3 results" tone="highlight" />
    </Svg>
  );
}

function RagRrf() {
  // Real rankings for "CT-112" from hybrid_demo.py's Index (55 chunks).
  const dense = ["R-0503", "R-0402", "R-0304", "R-0303", "R-0405", "R-0306", "R-0310", "FM-3.3", "R-0408", "R-0403", "R-0301"];
  const top = 58, step = 24, h = 20, w = 150, rx = 290;
  const y = (i: number) => top + i * step;
  return (
    <Svg viewBox="0 0 440 470" label="Dense search ranks R-0301 eleventh for CT-112; BM25 ranks it first; reciprocal rank fusion adds both and puts it first">
      <text className="dg-label" x={0} y={18}>Dense (meaning)</text>
      <text className="dg-note" x={0} y={38}>rank: chunk</text>
      <text className="dg-label" x={rx} y={18}>BM25 (words)</text>
      <text className="dg-note" x={rx} y={38}>rank: chunk</text>
      <line className="dg-arrow" x1={w} y1={y(10) + h / 2} x2={rx} y2={y(0) + h / 2} style={{ markerEnd: "none", opacity: 0.6 }} />
      <g className="dg-cells-small">
        {dense.map((id, i) => (
          <Box key={id} x={0} y={y(i)} w={w} h={h} label={`${i + 1}: ${id}`} tone={id === "R-0301" ? "highlight" : "plain"} code />
        ))}
        <Box x={rx} y={y(0)} w={w} h={h} label="1: R-0301" tone="highlight" code />
      </g>
      <text className="dg-note" x={rx} y={y(1) + 16}>the only chunk</text>
      <text className="dg-note" x={rx} y={y(1) + 34}>containing ct-112</text>
      <text className="dg-note" x={0} y={348}>Fused score: add 1 / (60 + rank) from each list.</text>
      <g className="dg-cells-small">
        <Box x={0} y={360} w={440} h={28} label="1st  R-0301: 1/71 + 1/61 = 0.0305" tone="highlight" code />
        <Box x={0} y={396} w={440} h={28} label="2nd  R-0503: 1/61 = 0.0164" code />
        <Box x={0} y={432} w={440} h={28} label="3rd  R-0402: 1/62 = 0.0161" code />
      </g>
    </Svg>
  );
}

function RagTwoStage() {
  // Real run of rerank_demo.py for the jeep question (55 chunks, 2 CPUs).
  const fused = ["FM-1.2", "R-0305", "FM-2.2", "FM-3.3", "FM-6.4", "R-0307", "FM-3.2", "FM-6.2"];
  const reranked: [string, string][] = [["FM-6.2", "-6.6"], ["R-0305", "-6.8"], ["FM-6.3", "-10.5"], ["R-0310", "-10.6"], ["FM-6.5", "-10.6"]];
  const top = 104, step = 26, h = 22, w = 170, rx = 270;
  const y = (i: number) => top + i * step;
  return (
    <Svg viewBox="0 0 440 432" label="Hybrid search ranks FM-6.2 eighth of 20 candidates for the jeep question; the cross-encoder reads all 20 with the question and puts FM-6.2 first">
      <text className="dg-note" x={0} y={16}>Can tourists get out of the jeep to take photos?</text>
      <text className="dg-label" x={0} y={54}>Stage 1: hybrid search</text>
      <text className="dg-note" x={0} y={74}>55 chunks to 20, under 0.1 s</text>
      <text className="dg-note" x={0} y={92}>fused order, first 8:</text>
      <text className="dg-label" x={rx} y={54}>Stage 2: cross-encoder</text>
      <text className="dg-note" x={rx} y={74}>reads all 20, about 1.4 s</text>
      <text className="dg-note" x={rx} y={92}>best 5 (score):</text>
      <line className="dg-arrow" x1={w} y1={y(7) + h / 2} x2={rx} y2={y(0) + h / 2} style={{ markerEnd: "none", opacity: 0.6 }} />
      <g className="dg-cells-small">
        {fused.map((id, i) => (
          <Box key={id} x={0} y={y(i)} w={w} h={h} label={`${i + 1}: ${id}`} tone={id === "FM-6.2" ? "highlight" : "plain"} code />
        ))}
        {reranked.map(([id, sc], i) => (
          <Box key={`r${id}`} x={rx} y={y(i)} w={w} h={h} label={`${i + 1}: ${id} (${sc})`} tone={id === "FM-6.2" ? "highlight" : "copy"} code />
        ))}
      </g>
      <text className="dg-note" x={0} y={y(8) + 16}>... 12 more candidates</text>
      <text className="dg-note" x={0} y={348}>Stage 1 only has to get FM-6.2 into the 20.</text>
      <text className="dg-note" x={0} y={368}>Stage 2 puts it first: its score is low, but the</text>
      <text className="dg-note" x={0} y={388}>highest of the 20 candidates.</text>
      <Box x={0} y={400} w={440} h={30} label="FM-6.2 Visitor rules: 8th, then 1st" tone="highlight" />
    </Svg>
  );
}

function RagGate() {
  // Real best reranker scores from two_stage(): the 26 test questions, and 8 questions the documents do not answer.
  const answered = [-8.0, -7.6, -6.6, 0.1, 1.2, 1.9, 2.2, 3.0, 3.7, 3.9, 4.0, 4.2, 4.4, 4.4, 4.6, 5.0, 5.1, 5.4, 5.5, 5.7, 6.4, 6.8, 7.0, 7.4, 8.9, 9.9];
  const missing = [-11.0, -10.7, -9.6, -8.1, -6.9, -2.1, 0.6, 3.3];
  const x = (v: number) => 20 + ((v + 12) / 22) * 400;
  const dots = (vals: number[], y: number, fill: string, k: string) =>
    vals.map((v, i) => <circle key={`${k}${i}`} cx={x(v)} cy={y + (i % 2 ? 7 : -7)} r={5} style={{ fill, stroke: "var(--figure-line)", strokeWidth: 1 }} />);
  return (
    <Svg viewBox="0 0 440 300" label="Best reranker scores on a number line: the 26 answered questions from -8.0 to 9.9, the 8 unanswerable ones from -11.0 to 3.3, and the gate at -9.0">
      <text className="dg-label" x={0} y={18}>Best reranker score of each question</text>
      <text className="dg-note" x={x(-9) + 6} y={44}>gate: -9.0</text>
      <line x1={x(-9)} y1={30} x2={x(-9)} y2={214} style={{ stroke: "var(--vermilion, #c63f28)", strokeWidth: 2, strokeDasharray: "5 4" }} />
      <text className="dg-note" x={x(-1)} y={72}>answered by the documents (26)</text>
      {dots(answered, 96, "var(--figure-green)", "a")}
      <text className="dg-note" x={x(-1)} y={146}>not in the documents (8)</text>
      {dots(missing, 170, "var(--figure-yellow)", "m")}
      <line x1={20} y1={214} x2={420} y2={214} className="dg-arrow" style={{ markerEnd: "none" }} />
      {[-12, -8, -4, 0, 4, 8].map((t) => (
        <g key={t}>
          <line x1={x(t)} y1={210} x2={x(t)} y2={218} className="dg-arrow" style={{ markerEnd: "none" }} />
          <text className="dg-note" x={x(t)} y={234} textAnchor="middle">{t}</text>
        </g>
      ))}
      <text className="dg-note" x={0} y={262}>Left of the gate: answered at once, no model call (3 questions).</text>
      <text className="dg-note" x={0} y={282}>Right of it: the model is asked, and its rules catch the rest.</text>
    </Svg>
  );
}

function RagEval() {
  // Real output of evaluate.py on the 26 test questions.
  const rows: [string, number, number, string][] = [
    ["keywords (chapter 1)", 50, 77, "4 ms"],
    ["dense (chapter 3)", 77, 92, "20 ms"],
    ["hybrid (chapter 9)", 58, 92, "23 ms"],
    ["hybrid + rerank (chapter 10)", 88, 100, "1,696 ms"],
  ];
  const W = 340;
  return (
    <Svg viewBox="0 0 440 372" label="Hit at 1 and hit at 5 for four pipelines on 26 questions: keywords 50 and 77, dense 77 and 92, hybrid 58 and 92, hybrid with rerank 88 and 100 percent">
      <rect x={0} y={4} width={14} height={12} className="dg-box" style={{ fill: "var(--figure-yellow)", stroke: "var(--figure-yellow-edge)" }} />
      <text className="dg-note" x={20} y={15}>hit@1: right chunk first</text>
      <rect x={210} y={4} width={14} height={12} style={{ fill: "var(--figure-green)", stroke: "var(--figure-green-edge)" }} />
      <text className="dg-note" x={230} y={15}>hit@5: in the top five</text>
      {rows.map(([name, h1, h5, ms], i) => {
        const y = 44 + i * 80;
        return (
          <g key={name}>
            <text className="dg-label" x={0} y={y}>{name}</text>
            <text className="dg-note" x={440} y={y} textAnchor="end">{ms} a question</text>
            <rect x={0} y={y + 8} width={(W * h1) / 100} height={18} rx={4} style={{ fill: "var(--figure-yellow)", stroke: "var(--figure-yellow-edge)", strokeWidth: 1.5 }} />
            <text className="dg-note" x={(W * h1) / 100 + 8} y={y + 22}>{h1}%</text>
            <rect x={0} y={y + 32} width={(W * h5) / 100} height={18} rx={4} style={{ fill: "var(--figure-green)", stroke: "var(--figure-green-edge)", strokeWidth: 1.5 }} />
            <text className="dg-note" x={(W * h5) / 100 + 8} y={y + 46}>{h5}%</text>
          </g>
        );
      })}
      <text className="dg-note" x={0} y={366}>Times: the lab machine's 2 CPUs, one run.</text>
    </Svg>
  );
}

function RagService() {
  // One POST /ask through app.py; times measured on the lab machine's 2 CPUs.
  const steps: [string, string, BoxTone][] = [
    ["POST /ask  {\"question\": ...}", "422 if the body is wrong", "plain"],
    ["index(): built once", "first request only: 6 to 9 s", "plain"],
    ["find(): hybrid search", "at most 40, then filters", "plain"],
    ["rerank the first 20", "70 ms each, about 1.4 s", "accent"],
    ["gate: best score below -9.0?", "yes: NOT_FOUND, no model call", "highlight"],
    ["model: lab-chat", "answer with [n] citations", "plain"],
    ["JSON  {answer, sources}", "back to the phone", "copy"],
  ];
  return (
    <Svg viewBox="0 0 440 408" label="A POST /ask request: FastAPI checks it, the index is built once, hybrid search finds candidates, the reranker orders 20, the gate may answer NOT_FOUND, otherwise the model answers with citations, and JSON goes back">
      {steps.map(([title, note, tone], i) => {
        const y = 4 + i * 58;
        return (
          <g key={title}>
            <g className="dg-cells-small"><Box x={0} y={y} w={216} h={34} label={title} tone={tone} code={i === 0 || i === 6} /></g>
            <text className="dg-note" x={228} y={y + 22}>{note}</text>
            {i < steps.length - 1 && <Arrow x1={108} y1={y + 36} x2={108} y2={y + 56} />}
          </g>
        );
      })}
    </Svg>
  );
}

const DIAGRAMS: Record<string, () => JSX.Element> = {
  "rag-flow": RagFlow,
  "rag-embed": RagEmbed,
  "rag-matrix": RagMatrix,
  "rag-chunks": RagChunks,
  "rag-ivf": RagIvf,
  "rag-hnsw": RagHnsw,
  "rag-binary": RagBinary,
  "rag-filter": RagFilter,
  "rag-rrf": RagRrf,
  "rag-two-stage": RagTwoStage,
  "rag-gate": RagGate,
  "rag-eval": RagEval,
  "rag-service": RagService,
  "rs-cli": RsCli,
  "rs-rc-refcell": RsRcRefCell,
  "rs-threads": RsThreads,
  "rs-async": RsAsync,
  "rs-speed": RsSpeed,
  "rs-capstone": RsCapstone,
  "rs-monomorph": RsMonomorph,
  "rs-trait-object": RsTraitObject,
  "rs-lifetime": RsLifetime,
  "rs-closure": RsClosure,
  "rs-iterator-chain": RsIteratorChain,
  "rs-test-mutation": RsTestMutation,
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
  "lc-wrap-tool": LcWrapTool,
  "lc-guards": LcGuards,
  "lc-long-memory": LcLongMemory,
  "lc-human-loop": LcHumanLoop,
  "lc-rag": LcRag,
  "lc-mcp": LcMcp,
  "lc-agent-loop": LcAgentLoop,
  "lc-memory-threads": LcMemoryThreads,
  "lc-ai-circles": LcAiCircles,
  "lc-tokens": LcTokens,
  "lc-cosine-matrix": LcCosineMatrix,
  "lc-next-token": LcNextToken,
  "lc-chat-request": LcChatRequest,
  "l4j-streaming": L4jStreaming,
  "l4j-memory-window": L4jMemoryWindow,
  "l4j-mcp": L4jMcp,
  "l4j-mcp-wire": L4jMcpWire,
  "l4j-routing": L4jRouting,
  "l4j-eval": L4jEval,
  "l4j-capstone-guard": L4jCapstoneGuard,
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
  "l4j-bigram-chain": L4jBigramChain,
  "l4j-grounding": L4jGrounding,
  "l4j-structured": L4jStructured,
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
