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
      <Box x={210} y={26} w={220} h={30} label="tea x2 | order_id 1" code />
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
    <Svg viewBox="0 0 440 200" label="Inside one transaction, the tea stock goes from 10 to 8, then the samosa check fails; the transaction rolls back and the tea stock is 10 again">
      <Box x={10} y={10} w={420} h={30} label="@Transactional placeOrder(tea x2, samosa x5)" tone="accent" code />
      <Box x={30} y={50} w={180} h={30} label="tea: 10 -> 8" />
      <Arrow x1={212} y1={65} x2={240} y2={65} />
      <Box x={244} y={50} w={186} h={30} label="samosa: only 1 left!" tone="highlight" />
      <Arrow x1={337} y1={82} x2={337} y2={110} />
      <Box x={244} y={114} w={186} h={30} label="exception: roll back" tone="highlight" />
      <Arrow x1={242} y1={129} x2={212} y2={129} />
      <Box x={30} y={114} w={180} h={30} label="tea: back to 10" tone="accent" />
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

const DIAGRAMS: Record<string, () => JSX.Element> = {
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
