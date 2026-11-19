// Offline code completion for the languages Monaco has no language service for (JavaScript and
// TypeScript already get the full one). Keywords, built-ins, the library calls the labs use, and
// snippets for the usual shapes. Instant, free, and it never writes a task's solution for you:
// it only finishes names, the learner still decides what the code does.
import { monaco } from "./monaco";

type Kind = "keyword" | "function" | "method" | "module" | "snippet" | "class" | "constant";
interface Item { label: string; kind: Kind; insert?: string; detail?: string }

const kw = (words: string, kind: Kind = "keyword", detail?: string): Item[] =>
  words.split(/\s+/).filter(Boolean).map((label) => ({ label, kind, detail }));
const fn = (words: string, detail: string): Item[] =>
  words.split(/\s+/).filter(Boolean).map((label) => ({ label, kind: "function", insert: `${label}($0)`, detail }));

const PYTHON: Item[] = [
  ...kw("False None True and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield"),
  ...fn("print len range enumerate zip sorted reversed sum min max abs round int float str bool list dict set tuple isinstance open input map filter any all repr type hasattr getattr", "built-in"),
  ...kw("collections json os sys time math random re datetime itertools functools pathlib typing", "module"),
  ...fn("Counter defaultdict OrderedDict deque namedtuple", "collections"),
  ...kw("append extend insert pop remove sort index count keys values items get update setdefault split join strip lower upper replace startswith endswith format", "method"),
  // the redis client (redis-py) and FastAPI, as used in the labs
  ...kw("get set incr decr expire ttl delete exists hset hget hgetall zadd zincrby zrange zrevrange lpush rpush lrange ping", "method", "redis"),
  ...kw("FastAPI HTTPException Depends Request", "class", "fastapi"),
  { label: "def", kind: "snippet", insert: "def ${1:name}(${2:args}):\n\t${0:pass}", detail: "function" },
  { label: "for", kind: "snippet", insert: "for ${1:item} in ${2:items}:\n\t$0", detail: "for loop" },
  { label: "if", kind: "snippet", insert: "if ${1:condition}:\n\t$0", detail: "if" },
  { label: "ifmain", kind: "snippet", insert: 'if __name__ == "__main__":\n\t$0', detail: "run as a script" },
  { label: "try", kind: "snippet", insert: "try:\n\t$1\nexcept ${2:Exception} as e:\n\t$0", detail: "try / except" },
  { label: "class", kind: "snippet", insert: "class ${1:Name}:\n\tdef __init__(self, $2):\n\t\t$0", detail: "class" },
  { label: "with", kind: "snippet", insert: "with open(${1:path}) as f:\n\t$0", detail: "open a file" },
  { label: "@app.get", kind: "snippet", insert: '@app.get("/${1:path}")\ndef ${2:handler}():\n\t$0', detail: "FastAPI route" },
];

const JAVA: Item[] = [
  ...kw("abstract boolean break byte case catch char class continue default do double else enum extends final finally float for if implements import instanceof int interface long new null package private protected public return short static super switch this throw throws try var void while true false record"),
  ...kw("String Integer Long Double Boolean List ArrayList Map HashMap Set HashSet Optional Math System Arrays Collections Objects StringBuilder", "class"),
  ...kw("add get put remove size isEmpty contains containsKey getOrDefault merge stream map filter collect toList forEach length charAt substring equals trim", "method"),
  ...kw("GetMapping PostMapping PutMapping DeleteMapping RestController RequestBody PathVariable RequestParam Service Autowired", "class", "Spring"),
  { label: "sout", kind: "snippet", insert: "System.out.println($0);", detail: "print a line" },
  { label: "main", kind: "snippet", insert: "public static void main(String[] args) {\n\t$0\n}", detail: "main method" },
  { label: "fori", kind: "snippet", insert: "for (int ${1:i} = 0; ${1:i} < ${2:n}; ${1:i}++) {\n\t$0\n}", detail: "counting loop" },
  { label: "foreach", kind: "snippet", insert: "for (${1:var} ${2:item} : ${3:items}) {\n\t$0\n}", detail: "for each" },
  { label: "if", kind: "snippet", insert: "if (${1:condition}) {\n\t$0\n}", detail: "if" },
];

const GO: Item[] = [
  ...kw("break case chan const continue default defer else fallthrough for func go goto if import interface map package range return select struct switch type var nil true false"),
  ...fn("len cap append make new delete copy panic recover", "built-in"),
  ...kw("int int64 float64 string bool byte rune error any", "class"),
  ...kw("fmt strings strconv errors sort time os", "module"),
  ...kw("Println Printf Sprintf Errorf Split Join Contains TrimSpace Atoi Itoa ParseFloat New Slice Sort", "function"),
  { label: "func", kind: "snippet", insert: "func ${1:name}(${2:args}) ${3:error} {\n\t$0\n}", detail: "function" },
  { label: "forr", kind: "snippet", insert: "for ${1:i}, ${2:v} := range ${3:items} {\n\t$0\n}", detail: "range loop" },
  { label: "iferr", kind: "snippet", insert: "if err != nil {\n\treturn ${1:err}\n}", detail: "check the error" },
];

const SQL: Item[] = [
  ...kw("SELECT FROM WHERE AND OR NOT IN IS NULL LIKE ILIKE BETWEEN ORDER BY GROUP HAVING LIMIT OFFSET AS JOIN LEFT RIGHT INNER OUTER ON DISTINCT INSERT INTO VALUES UPDATE SET DELETE CREATE TABLE INDEX ALTER ADD DROP CONSTRAINT PRIMARY KEY FOREIGN REFERENCES CHECK UNIQUE DEFAULT BEGIN COMMIT ROLLBACK EXPLAIN ANALYZE CASE WHEN THEN ELSE END RETURNING WITH DESC ASC"),
  ...fn("COUNT SUM AVG MIN MAX COALESCE NOW LOWER UPPER LENGTH ROUND DATE_TRUNC EXTRACT", "function"),
  ...kw("pg_stat_activity pg_locks pg_blocking_pids pg_terminate_backend pg_cancel_backend", "function", "postgres"),
  ...kw("integer bigint text varchar boolean timestamptz numeric serial", "class", "type"),
];

const SHELL: Item[] = [
  ...kw("if then else elif fi for in do done while case esac function return exit export local"),
  ...kw("echo cat grep awk sed sort uniq head tail wc cut tr find xargs du df ls chmod chown truncate curl ps kill", "function", "command"),
  { label: "shebang", kind: "snippet", insert: "#!/usr/bin/env bash\nset -euo pipefail\n$0", detail: "script header" },
];

const BY_LANGUAGE: Record<string, Item[]> = { python: PYTHON, java: JAVA, go: GO, sql: SQL, shell: SHELL };

const KINDS = (): Record<Kind, monaco.languages.CompletionItemKind> => {
  const k = monaco.languages.CompletionItemKind;
  return { keyword: k.Keyword, function: k.Function, method: k.Method, module: k.Module, snippet: k.Snippet, class: k.Class, constant: k.Constant };
};

let registered = false;

export function registerCompletions(): void {
  if (registered) return;
  registered = true;
  const kinds = KINDS();
  for (const [language, items] of Object.entries(BY_LANGUAGE)) {
    monaco.languages.registerCompletionItemProvider(language, {
      provideCompletionItems(model, position) {
        const word = model.getWordUntilPosition(position);
        const range = { startLineNumber: position.lineNumber, endLineNumber: position.lineNumber, startColumn: word.startColumn, endColumn: word.endColumn };
        return {
          suggestions: items.map((it) => ({
            label: it.label,
            kind: kinds[it.kind],
            detail: it.detail,
            insertText: it.insert ?? it.label,
            insertTextRules: it.insert ? monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet : undefined,
            range,
          })),
        };
      },
    });
  }
}
