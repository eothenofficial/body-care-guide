# A抽象线描与同形图标

用户已选择此前方案A。PNG直接复用选定图，不重新生成新人物。原图为内置image_gen生成，品牌图标采用同一抽象侧脸的SVG简化轮廓；移除“护”字和绿色实心底框。桌面字号、框架及医学正文保持；手机按SOP第38节独立布局。

- 选定原图：`home-portrait-abstract.png`。通过CSS控制显示比例，未修改原始PNG像素。
- 手机在首页标题旁保留小幅同图，不隐藏或挤压完整介绍；深色手机界面用受控CSS invert/sepia提高线条对比，不改PNG字节。普通桌面表现保留。
- 独立SVG：`brand-abstract.svg`；页面使用同一路径的内嵌symbol，能随浅深色主题改变墨色。
- favicon：`../favicon.svg`。线条略粗，增加纸色底，以利浏览器页签的小尺寸显示。
- 正式书名《少走弯路的人体保养指南》及两段首页介绍已获用户明确批准，当前版本按`drafts/whole-body/approved-home-20261030/home-copy.json`逐字落实；A图形不变。

选定原图的完整生成提示词：

> Use case: illustration-story. Candidate A, an extremely economical Pablo Picasso inspired modernist line drawing. One head-and-shoulders portrait of a fully clothed adult person wearing a closed-collar plain shirt or simple jacket. Draw the shirt collar explicitly. Suggest the face from overlapping profile and front view using about ten confident thin black ink curves with elegant negative space. Sparse, abstract, asymmetrical and plainly hand-drawn. Black ink only, no filled skin or hair areas, no shading, no color patches, no accessories, no fashion glamour, no watercolor, no background shapes, no text. Keep the small portrait in the central half of a square transparent canvas with very large empty margins. A quiet supporting drawing for a nonfiction reference website, intended to display at 160px wide.
