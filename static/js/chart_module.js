function createLineChart(containerId, xData, yData1, yData2, seriesNames) {
    // 确保 AnyChart 文档加载完成后运行
    anychart.onDocumentReady(function () {
        // 验证输入数据长度是否一致
        if (xData.length !== yData1.length || xData.length !== yData2.length) {
            console.error("输入数据长度不一致！");
            return;
        }

        // 构造数据
        var data = [];
        for (var i = 0; i < xData.length; i++) {
            data.push([xData[i], yData1[i], yData2[i]]);
        }

        // 创建数据集
        var dataSet = anychart.data.set(data);

        // 映射数据到系列
        var firstSeriesData = dataSet.mapAs({ x: 0, value: 1 });
        var secondSeriesData = dataSet.mapAs({ x: 0, value: 2 });

        // 创建折线图
        var chart = anychart.line();

        // 设置图表背景颜色
        chart.background().fill("#121111"); // 设置背景颜色为浅灰色

        // 设置纵坐标的最小值为 -5
        chart.yScale().minimum(-5);

        // 手动设置刻度值，从 0 开始
        chart.yScale().ticks().set([0, 5, 10, 15, 20,25,30,40,45,50,55,60,65,70,75,80]); // 自定义刻度值

        // 创建系列并命名
        var firstSeries = chart.line(firstSeriesData);
        firstSeries.name(seriesNames[0] || "Series 1");
        firstSeries.stroke("#FF5733"); // 设置第一条折线的颜色为橙红色

        var secondSeries = chart.line(secondSeriesData);
        secondSeries.name(seriesNames[1] || "Series 2");
        secondSeries.stroke("#33FF57"); // 设置第二条折线的颜色为绿色

        // 启用图例
        chart.legend().enabled(true);

        // 添加标题
        chart.title("本月运动量和计划运动量");

        // 设置图表容器
        chart.container(containerId);

        // 绘制图表
        chart.draw();
    });
}