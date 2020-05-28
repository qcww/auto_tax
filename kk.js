var selectPzxhId = "";
var selectPzxh = "";
var qse = 0;
var znj = 0;
var loaded = false;
var loaded2 = false;
$(function() {
    loadWjkList();
    loadSfxyList()
});
function loadWjkList() {
    $_ajax({
        url: ctx + "/wssb/ybzsjk/wjkListData",
        data: {
            swjgdm: $("#zgswjgDm").val()
        },
        success: function(a) {
            createTable(a);
            loaded = true
        }
    })
}
function loadSfxyList() {
    $_ajax({
        url: ctx + "/wssb/ybzsjk/sfxyhListData",
        success: function(a) {
            createTable2(a);
            loaded2 = true
        }
    })
}
function doJk() {
    if (oneCheckFormData()) {
        var a = $("#bckpje").val();
        $.confirm("本次开具金额为：<span class='as-red' style='font-weight: 600;font-size: 18px;'>" + a + "元 </span>。您确定要进行缴款吗？",
        function(b) {
            skyJk();
            $.close(b)
        })
    }
}
function yljk() {
    var b = $("#wjkTable").bootstrapTable("getSelections");
    if (!loaded || b.length == 0) {
        $.alert("请选择缴款项目！");
        return false
    }
    var a = $("#bckpje").val();
    $.confirm("本次开具金额为：<span class='as-red' style='font-weight: 600;font-size: 18px;'>" + a + "元 </span>。您确定要进行缴款吗？",
    function(c) {
        $_ajax({
            type: "POST",
            url: ctx + "/wssb/ybzsjk/unionPayment",
            data: getTjsj(),
            success: function(f) {
                var e = f.hxpayUrl;
                var d = f.orderId;
                yljkCommitFunc(e, d, null)
            }
        });
        $.close(c)
    })
}
function yljkCommitFunc(b, a, c) {
    confirmYljk(b + "?orderId=" + a, c)
}
function confirmYljk(a, b) {
    window.open(a);
    $.confirm("<div style='font-size:18px;color:#f00'>银联缴款是否成功？</div><div style='margin-top:5px;color:#999;'>若长时间未显示银联缴款窗口，请检查当前浏览器是否拦截了弹出窗口。</div>", {
        title: "提示",
        closeBtn: false,
        btn: ["是", "否"]
    },
    function() {
        window.location.reload()
    },
    function() {
        $.alert("请重新缴款",
        function() {
            window.location.reload()
        })
    })
}
function skyJk() {
    $_ajax({
        type: "POST",
        url: ctx + "/wssb/ybzsjk/skyJk",
        data: getTjsj(),
        success: function(a) {
            $.alert("税库银联网缴款成功!",
            function() {
                window.location.reload()
            })
        }
    })
}
function oneCheckFormData() {
    var d = $("#wjkTable").bootstrapTable("getSelections");
    if (!loaded || d.length == 0) {
        $.alert("请选择缴款项目！");
        return false
    }
    var b = $("#sfxyTable").bootstrapTable("getSelections");
    if (!loaded2 || b.length == 0) {
        $.alert("请选择缴款账户!");
        return false
    } else {
        $("#sfxyh").val(b[0].sfxyh)
    }
    var c = b[0].skssswjgDm;
    for (var a = 0; a < d.length; a++) {
        if (d[a].skssswjgDm != c) {
            $.alert("您所选择的缴款项目税款所属税务机构跟三方协议税款所属税务机构不一致，请重新选择！");
            return false
        }
    }
    return true
}
function createTable(a) {
    $("#wjkTable").bootstrapTable("destroy").bootstrapTable({
        data: a,
        striped: true,
        pageNumber: 1,
        pagination: false,
        pageSize: 10,
        pageList: [10],
        showRefresh: false,
        showColumns: false,
        clickToSelect: true,
        columns: columns,
        locale: "zh-CN",
        showFooter: false,
        checkboxHeader: false,
        onCheck: function(e) {
            $("#djxh").val(e.djxh);
            var d = $("#wjkTable").bootstrapTable("getData");
            var b = e.yzpzxh;
            for (var c = 0; c < d.length; c++) {
                if (b == d[c].yzpzxh) {
                    if (!d[c].xz) {
                        d[c].xz = true
                    }
                } else {
                    d[c].xz = false
                }
            }
            $("#wjkTable").bootstrapTable("load", d);
            setFooterSe()
        },
        onUncheck: function(b) {
            setFooterSe()
        }
    })
}
function createTable2(a) {
    $("#sfxyTable").bootstrapTable("destroy").bootstrapTable({
        data: a,
        striped: true,
        pageNumber: 1,
        pagination: false,
        pageSize: 10,
        pageList: [10],
        showRefresh: false,
        showColumns: false,
        clickToSelect: true,
        singleSelect: true,
        columns: columns2,
        locale: "zh-CN",
        showFooter: false
    })
}
var columns = [{
    field: "xz",
    checkbox: true
},
{
    title: "序号",
    field: "name",
    align: "center",
    valign: "middle",
    formatter: function(b, c, a) {
        return a + 1
    }
},
{
    title: "凭证序号",
    field: "yzpzxh",
    align: "center",
    valign: "middle",
    formatter: function(b, c, a) {
        return "<div style='width:180px;'>" + b + "</div>"
    }
},
{
    title: "凭证种类",
    field: "yzpzzlMc",
    align: "center",
    valign: "middle",
    formatter: function(b, c, a) {
        return "<div style='width:220px;padding:0 5px;line-height:20px;'>" + b + "</div>"
    }
},
{
    title: "征收项目",
    field: "zsxmMc",
    align: "center",
    valign: "middle",
    formatter: function(b, c, a) {
        return "<div style='width:140px;padding:0 5px;'>" + b + "</div>"
    }
},
{
    title: "征收品目",
    field: "zspmMc",
    align: "center",
    valign: "middle",
    formatter: function(b, c, a) {
        return "<div style='width:200px;padding:0 5px;line-height:20px;'>" + b + "</div>"
    }
},
{
    title: "税额",
    field: "ybtse",
    align: "center",
    valign: "middle",
    formatter: function(b, c, a) {
        return "<div style='width:100px;padding:0 5px;'>" + Number(b).toFixed2(2) + "</div>"
    }
},
{
    title: "所属期起",
    field: "skssqq",
    align: "center",
    valign: "middle",
    formatter: function(b, c, a) {
        return "<div style='width:100px;padding:0 5px;'>" + b.substr(0, 10) + "</div>"
    }
},
{
    title: "所属期止",
    field: "skssqz",
    align: "center",
    valign: "middle",
    formatter: function(b, c, a) {
        return "<div style='width:100px;padding:0 5px;'>" + b.substr(0, 10) + "</div>"
    }
},
{
    title: "缴款期限",
    field: "jkqx",
    align: "center",
    valign: "middle",
    formatter: function(b, c, a) {
        return "<div style='width:100px;padding:0 5px;'>" + b.substr(0, 10) + "</div>"
    }
},
{
    title: "申报日期",
    field: "nssbrq",
    align: "center",
    valign: "middle",
    formatter: function(b, c, a) {
        return "<div style='width:100px;padding:0 5px;'>" + b.substr(0, 10) + "</div>"
    }
}];
var columns2 = [{
    field: "xz",
    radio: true
},
{
    title: "序号",
    field: "name",
    align: "center",
    valign: "middle",
    formatter: function(b, c, a) {
        return a + 1
    }
},
{
    title: "三方协议号",
    field: "sfxyh",
    align: "center",
    valign: "middle"
},
{
    title: "银行行别",
    field: "yhhbMc",
    align: "center",
    valign: "middle"
},
{
    title: "银行营业网点",
    field: "yhyywdMc",
    align: "center",
    valign: "middle"
},
{
    title: "缴款帐号",
    field: "jkzh",
    align: "center",
    valign: "middle"
},
{
    title: "缴款账户名称",
    field: "jkzhmc",
    align: "center",
    valign: "middle"
},
{
    title: "税款所属税务机构",
    field: "skssswjgMc",
    align: "center",
    valign: "middle"
}];
function getTjsj() {
    var c = $("#mainForm").serialize();
    var a = $("#wjkTable").bootstrapTable("getSelections");
    for (var b = 0; b < a.length; b++) {
        c += "&yzpzxh=" + a[b].yzpzxh;
        c += "&ybtse=" + a[b].ybtse;
        c += "&znjLrExt=" + a[b].znjLrExt;
        c += "&zsuuid=" + a[b].zsuuid;
        c += "&yzpzmxxh=" + a[b].yzpzmxxh;
        c += "&yzpzzlDm=" + a[b].yzpzzlDm;
        c += "&skssswjg=" + a[b].skssswjgDm;
        c += "&skssqq=" + a[b].skssqq.substr(0, 10);
        c += "&skssqz=" + a[b].skssqz.substr(0, 10)
    }
    return c
}
function flushData() {
    $_ajax({
        type: "POST",
        url: ctx + "/wssb/ybzsjk/flushSfxxData",
        success: function(a) {
            $.alert("刷新成功！",
            function(b) {
                $.close(b);
                loadSfxyList()
            })
        }
    })
}
function setFooterSe() {
    var b = $("#wjkTable").bootstrapTable("getData");
    var d = "0.00";
    var c = "0.00";
    for (var a = 0; a < b.length; a++) {
        if (b[a].xz) {
            d = Number(d).add(Number(b[a].znjLrExt)).toFixed2(2);
            c = Number(c).add(Number(b[a].ybtse)).toFixed2(2)
        }
    }
    $("#se").val(c);
    $("#znj").val(d);
    $("#bckpje").val(Number(c).add(Number(d)).toFixed2(2))
}
function ghjfpzkj() {
    var c = $("#wjkTable").bootstrapTable("getSelections");
    if (!loaded || c.length == 0) {
        $.alert("请选择缴款项目！");
        return false
    }
    var a = c[0].skssswjgDm;
    for (var b = 0; b < c.length; b++) {
        if (! (c[b].zspmMc == "工会经费" || c[b].zspmMc == "工会经费滞纳金、罚款")) {
            $.alert("该功能只支持工会经费银行端缴款凭证开具，请确认！");
            return false
        }
        if (c[b].skssswjgDm != a) {
            $.alert("您所选择的缴款项目税款所属税务机构跟三方协议税款所属税务机构不一致，请重新选择！");
            return false
        }
    }
    alert("该功能需要打印缴款凭证后到银行柜台办理扣款");
    $.confirm("是否打印银行账户信息？", {
        btn: ["是", "否"]
    },
    function(d) {
        $_ajax({
            url: ctx + "/wssbAjax/cxsbjfrckzhxx",
            data: {
                djxh: $("#djxh").val()
            },
            type: "POST",
            async: false,
            success: function(h) {
                h = JSON.parse(h);
                if (h && h.ckzhzhbgGrid && h.ckzhzhbgGrid.ckzhzhbgGridlb) {
                    var f = Object.prototype.toString.call(h.ckzhzhbgGrid && h.ckzhzhbgGrid.ckzhzhbgGridlb) == "[object Array]";
                    var e = [];
                    if (f) {
                        for (var g = 0; g < h.ckzhzhbgGrid.ckzhzhbgGridlb.length; g++) {
                            if (h.ckzhzhbgGrid.ckzhzhbgGridlb[g].sbfzhbz != "Y") {
                                e.push({
                                    fkrmc: h.ckzhzhbgGrid.ckzhzhbgGridlb[g].zhmc,
                                    yhyywdDm: h.ckzhzhbgGrid.ckzhzhbgGridlb[g].yhyywdDm,
                                    fkrzh: h.ckzhzhbgGrid.ckzhzhbgGridlb[g].yhzh
                                })
                            }
                        }
                    } else {
                        if (h.ckzhzhbgGrid.ckzhzhbgGridlb.sbfzhbz != "Y") {
                            e.push({
                                fkrmc: h.ckzhzhbgGrid.ckzhzhbgGridlb.zhmc,
                                yhyywdDm: h.ckzhzhbgGrid.ckzhzhbgGridlb.yhyywdDm,
                                fkrzh: h.ckzhzhbgGrid.ckzhzhbgGridlb.yhzh
                            })
                        }
                    }
                    if (e.length < 1) {
                        alert("未查询到有效的存款账户账号报告信息，可通过【综合信息报告】-【制度信息报告】-【存款账户账号报告】办理");
                        return false
                    }
                    $.open({
                        type: 1,
                        title: "请选择银行信息",
                        content: "<div class='panel-body'><table id='msjs'></table><br/><div style='text-align:center;'><button type='button' onclick='gfjhpzkj()'>确定</button></div></div>",
                        success: function() {
                            $("#msjs").bootstrapTable("destroy").bootstrapTable({
                                data: e,
                                striped: true,
                                pageNumber: 1,
                                pagination: false,
                                pageSize: 10,
                                pageList: [10],
                                showRefresh: false,
                                showColumns: false,
                                clickToSelect: true,
                                singleSelect: true,
                                columns: [{
                                    radio: true
                                },
                                {
                                    title: "银行账户名称",
                                    field: "fkrmc",
                                    align: "center",
                                    valign: "middle"
                                },
                                {
                                    title: "银行账户",
                                    field: "fkrzh",
                                    align: "center",
                                    valign: "middle"
                                },
                                {
                                    title: "银行营业网点代码",
                                    field: "yhyywdDm",
                                    align: "center",
                                    valign: "middle"
                                }],
                                locale: "zh-CN",
                                showFooter: false
                            })
                        }
                    })
                } else {
                    alert("未查询到有效的存款账户账号报告信息，可通过【综合信息报告】-【制度信息报告】-【存款账户账号报告】办理");
                    return false
                }
            }
        });
        $.close(d)
    },
    function(d) {
        gfjhpzkj();
        $.close(d)
    })
}
function gfjhpzkj() {
    var f = $("#wjkTable").bootstrapTable("getSelections");
    var b = f[0].skssswjgDm;
    var e = getTjsj();
    e += "&pzkj=1";
    e += "&SKSSSWJG_DM=" + b;
    var a = $("#msjs").bootstrapTable("getData");
    if (a.length > 0) {
        var d = false;
        for (var c = 0; c < a.length; c++) {
            if (a[c][0] == true) {
                e += "&fkrzh=" + a[c].fkrzh;
                e += "&yhyywdDm=" + a[c].yhyywdDm;
                e += "&fkrmc=" + a[c].fkrmc;
                d = true
            }
        }
        if (d == false) {
            alert("请选择银行信息");
            return false
        }
    } else {
        e += "&fkrzh=";
        e += "&yhyywdDm=";
        e += "&fkrmc="
    }
    $_ajax({
        type: "POST",
        url: ctx + "/wssb/ybzsjk/sbfpzkj",
        data: e,
        async: true,
        success: function(j) {
            var h = "SBFPZKJ";
            var g = j.print_server + "/wssbExport/pzkj?skssswjg=" + j.sbfkjxx[0].dcxx.skssswjgDm;
            alert("凭证开具后“银行卡缴纳异常处理”菜单中会生成一条记录，请不要做“撤销”处理，否则会影响税款缴纳，携带凭证等相关资料去银行缴款即可。");
            var i = $("<form enctype='multipart/form-data'></form>").attr("action", g).attr("method", "post");
            i.append($("<input></input>").attr("type", "hidden").attr("name", "xml").attr("value", JSON.stringify(j.sbfkjxx)));
            i.append($("<input></input>").attr("type", "hidden").attr("name", "bddm").attr("value", h));
            i.append($("<input></input>").attr("type", "hidden").attr("name", "fileName").attr("value", "银行端缴款凭证"));
            i.appendTo("body").submit().remove();
            $.close();
            loadWjkList()
        }
    })
};