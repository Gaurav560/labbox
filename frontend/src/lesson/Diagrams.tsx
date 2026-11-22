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
      <Box x={210} y={26} w={220} h={30} label="lassi x2 | order_id 1" code />
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
    <Svg viewBox="0 0 440 200" label="Inside one transaction, the lassi stock goes from 10 to 8, then the samosa check fails; the transaction rolls back and the lassi stock is 10 again">
      <Box x={10} y={10} w={420} h={30} label="@Transactional placeOrder(lassi x2, samosa x5)" tone="accent" code />
      <Box x={30} y={50} w={180} h={30} label="lassi: 10 -> 8" />
      <Arrow x1={212} y1={65} x2={240} y2={65} />
      <Box x={244} y={50} w={186} h={30} label="samosa: only 1 left!" tone="highlight" />
      <Arrow x1={337} y1={82} x2={337} y2={110} />
      <Box x={244} y={114} w={186} h={30} label="exception: roll back" tone="highlight" />
      <Arrow x1={242} y1={129} x2={212} y2={129} />
      <Box x={30} y={114} w={180} h={30} label="lassi: back to 10" tone="accent" />
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

const DIAGRAMS: Record<string, () => JSX.Element> = {
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
