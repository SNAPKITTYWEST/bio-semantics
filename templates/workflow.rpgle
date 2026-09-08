**free
ctl-opt dftactgrp(*no) actgrp(*caller);

dcl-pr RunDeclaredStage extpgm('RUNSTAGE');
  workflowId char(64) const;
  runId      char(64) const;
  stageId    char(32) const;
  manifestId char(128) const;
  stageStatus char(16);
end-pr;

dcl-pi *n;
  workflowId char(64) const;
  runId      char(64) const;
  manifestId char(128) const;
end-pi;

dcl-s stageStatus char(16) inz('NOT_RUN');

// RUNSTAGE is a required external adapter, not supplied here.
// It resolves the immutable manifest, invokes the declared stage,
// and records source/destination identities and actual execution evidence.
RunDeclaredStage(workflowId : runId : 'PYTHON_PIPELINE' :
                 manifestId : stageStatus);

if stageStatus <> 'SUCCEEDED';
  dsply ('Workflow status: ' + %trim(stageStatus));
endif;

*inlr = *on;
return;
