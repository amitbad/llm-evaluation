# Bug tracker

Local fixes below are ready for review. Production checks were read-only against release `aa01ca7`.

| Bug ID | Description | Severity | Status | Affected file/component | Resolution or next action |
| --- | --- | --- | --- | --- | --- |
| QA-01 | The live homepage workbook link and Test 2 report link return 404, although both files pass local release validation. | High | Open | Public exercise routes | Restore both exact routes and verify the workbook download and report over HTTPS. |
| QA-02 | Legacy `/docs/` URLs return 404. The published homepage and curriculum identified these paths as canonical. | Medium | Canonicals fixed locally | Homepage and curriculum metadata, public URL aliases | Canonicals now use the working root-level routes. Review redirects for previously shared URLs. |
| QA-03 | The curriculum skip link can sit under the sticky header. Vertical tabs omit Up and Down handling, and mobile keyboard activation closes the sidebar. | Medium | Fixed locally | Curriculum generator and shared navigation | Raised the skip link above the header and added vertical keyboard handling. The mobile menu still closes on pointer clicks. |
| QA-04 | Dark theme hover uses dark icons on a dark sidebar. The theme button can announce the opposite theme as pressed. | Medium | Fixed locally | Shared theme CSS and JavaScript | Kept the theme palette through hover and gave the button an explicit action label. |
| QA-05 | Concepts Reference uses visual headings without a semantic page outline. The concepts and curriculum pages lack search descriptions. | Low | Fixed locally | Concepts Reference and curriculum generator | Added a heading hierarchy to Concepts Reference and page descriptions to both. |
| QA-06 | The 14 individual lesson pages lack descriptions and canonical tags. The live sitemap and robots.txt routes return 404. | Low | Open | Lesson metadata and public search discovery | Add lesson-specific metadata and review sitemap and crawler policy against the working production URLs. |
| QA-07 | Quick Learning topic and prerequisite links sent learners to Complete Course, where the path and lesson position were easy to lose. | High | Fixed locally | Guided navigation and progress | Use readable lesson titles, path-specific URLs, and breadcrumbs. Show the same topic material in both modes and keep a return link when switching modes. |

## Unverified behavior

- Owner browser acceptance remains pending for mobile and desktop navigation, keyboard interaction, native progress persistence and file transfers, and roadmap visual rendering and exports.
- Live VPS configuration, certificate renewal, and publish and rollback behavior were outside this QA.
- Review the Complete Course disclosure hierarchy with a screen reader. Its repository mapping headings sit below topic summaries, which may make the heading list harder to navigate.

Record confirmed issues in the table when discovered. Update the same entry when fixed or reopened, and keep its resolution history.
