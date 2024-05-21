$(document).ready(function() {
    $("#add-column").click(function() {
        let formId = $("#id_column_set-TOTAL_FORMS").val();
        let emptyFormHtml = $("#empty-form").html();
        $("#form-set").append(emptyFormHtml.replace(/__prefix__/g, formId));
        $("#id_column_set-TOTAL_FORMS").val(parsInt(formId) + 1);
        $("[id$='type']").change((e) => {
            range_appear(e.target)
    })
})
$("[id$='type']").each(function() {
            range_appear($(this))
    })
})


const range_appear = (columnType) => {
    let row = $(columnType).parents(".form-inline");
    let from = $(row).find("[id$='range_from']");
    let to = $(row).find("[id$='range_to']");
    if ($(columnType).val() === "2" || $(columnType).val() === "3") {
          from.parents(".form-group").show();
          to.parents(".form-group").show();
    }else{
    from.parents(".form-group").hide();
    to.parents(".form-group").hide();
    }
}