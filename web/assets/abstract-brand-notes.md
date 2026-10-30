# A抽象线描与同形图标

用户已选择此前方案A。右侧PNG直接复用选定图，不重新生成新人物。原图为内置image_gen生成，图标改为同一抽象侧脸的SVG简化轮廓；移除“护”字和绿色实心底框。字号、布局和主正文保持。

- 选定原图：`home-portrait-abstract.png`。通过CSS控制显示比例，未修改原始PNG像素。
- 独立SVG：`brand-abstract.svg`；页面使用同一路径的内嵌symbol，能随浅深色主题改变墨色。
- favicon：`../favicon.svg`。线条略粗，增加纸色底，以利浏览器页签的小尺寸显示。
- 正式书名《少走弯路的人体保养指南》及两段首页介绍已获用户明确批准，当前版本按`drafts/whole-body/approved-home-20261030/home-copy.json`逐字落实；A图形不变。

选定原图的完整生成提示词：

> Use case: illustration-story. Candidate A, an extremely economical Pablo Picasso inspired modernist line drawing. One head-and-shoulders portrait of a fully clothed adult person wearing a closed-collar plain shirt or simple jacket. Draw the shirt collar explicitly. Suggest the face from overlapping profile and front view using about ten confident thin black ink curves with elegant negative space. Sparse, abstract, asymmetrical and plainly hand-drawn. Black ink only, no filled skin or hair areas, no shading, no color patches, no accessories, no fashion glamour, no watercolor, no background shapes, no text. Keep the small portrait in the central half of a square transparent canvas with very large empty margins. A quiet supporting drawing for a nonfiction reference website, intended to display at 160px wide.
