---
title: Review Skipped resources from Feature Teardown
assignees: Kremzeeq
labels: Review
---

Cloudformation Stack: ${{ env.APP }}-${{ env.ENV }}
FORCE_DELETE_STACK has been executed. This skips resources which fail to delete.
Review any retained resources with the status DELETE_SKIPPED: ${{ needs.feature-cloudformation-stack-teardown.outputs.payload }}
