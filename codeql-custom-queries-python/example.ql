import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.TaintTracking

predicate isExecutedAsSQL(Expr arg) {
    exists(Call c, Attribute att |
        c.getLocation().getFile().getBaseName() = "app.py"
        and c.getFunc() = att
        and att.getName() = "execute"
        and arg = c.getArg(0)
    )
  }

predicate isUserInput(Expr arg) {
    exists(Call c, Attribute att |
        c.getLocation().getFile().getBaseName() = "app.py"
        and c.getFunc() = att
        and att.getName() = "get"
        and arg = c
    )
  }

module SimpleSQLConfig implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node source) {
    isUserInput(source.asExpr())
  }

  predicate isSink(DataFlow::Node sink) {
    isExecutedAsSQL(sink.asExpr())
  }
}

module SimpleSQLFlow = TaintTracking::Global<SimpleSQLConfig>;

from DataFlow::Node source, DataFlow::Node sink
where SimpleSQLFlow::flow(source, sink)
select sink, "This SQL query depends on a $@.", source, "user-provided value"