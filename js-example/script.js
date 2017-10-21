/*
  This script was copied verbatim from ServiceNow Guru:
  https://www.servicenowguru.com/system-definition/exporting-service-catalog-items-step/
 */

(function process(g_request, g_response, g_processor) {
    var sysid = g_request.getParameter('sysparm_sys_id');
    gs.log('** Exporting Catalog Item ' + sysid);

    //Name all the related lists
    var exporter = new ExportWithRelatedLists('sc_cat_item', sysid);
    exporter.addRelatedList('item_option_new', 'cat_item');
    exporter.addRelatedList('catalog_script_client', 'cat_item');
    exporter.addRelatedList('catalog_ui_policy', 'catalog_item');
    exporter.addRelatedList('sc_cat_item_category', 'sc_cat_item');
    exporter.addRelatedList('sc_cat_item_catalog', 'sc_cat_item');
    exporter.addRelatedList('sc_cat_item_user_criteria_mtom', 'sc_cat_item');
    exporter.addRelatedList('sc_cat_item_user_criteria_no_mtom', 'sc_cat_item');
    exporter.addRelatedList('sc_cat_item_group_mtom', 'sc_cat_item');
    exporter.addRelatedList('sc_cat_item_group_no_mtom', 'sc_cat_item');
    exporter.addRelatedList('sc_cat_item_company_mtom', 'sc_cat_item');
    exporter.addRelatedList('sc_cat_item_company_no_mtom', 'sc_cat_item');
    exporter.addRelatedList('sc_cat_item_dept_mtom', 'sc_cat_item');
    exporter.addRelatedList('sc_cat_item_dept_no_mtom', 'sc_cat_item');
    exporter.addRelatedList('sc_cat_item_location_mtom', 'sc_cat_item');
    exporter.addRelatedList('sc_cat_item_location_no_mtom', 'sc_cat_item');
    exporter.addRelatedList('sc_cat_item_user_mtom', 'sc_cat_item');
    exporter.addRelatedList('sc_cat_item_user_no_mtom', 'sc_cat_item');
    exporter.addRelatedList('sc_cat_item_app_group', 'sc_cat_item');
    exporter.addRelatedList('sc_cat_item_app_user', 'sc_cat_item');
    exporter.addRelatedList('sc_cat_item_guide_items', 'guide');
    exporter.addRelatedList('pc_vendor_cat_item', 'product_catalog_item');

    var catalogID = '';
    var categoryID = '';
    var vsrelID = '';
    var vsID = '';
    var vID = '';
    var qcID = '';
    var uipID = '';
    var actID = '';
    var csID = '';

    //Query for Catalogs
    var catalog = new GlideRecord('sc_cat_item_catalog');
    catalog.addQuery('sc_cat_item', sysid);
    catalog.query();
    while(catalog.next()){
        //Get Catalog IDs
        catalogID = catalogID + ',' + catalog.sc_catalog.sys_id.toString();
    }

    //Query for Categories
    var category = new GlideRecord('sc_cat_item_category');
    category.addQuery('sc_cat_item', sysid);
    category.query();
    while(category.next()){
        //Get Category IDs
        categoryID = categoryID + ',' + category.sc_category.sys_id.toString();
    }

    //Query for variables to get question choices
    var item = new GlideRecord('item_option_new');
    item.addQuery('cat_item', sysid);
    item.query();
    while(item.next()){
        //Query for question choices
        var qc = new GlideRecord('question_choice');
        qc.addQuery('question', item.sys_id.toString());
        qc.query();
        while(qc.next()){
            //Add the variable question sys_id to the variable question string
            qcID = qcID + ',' + qc.sys_id.toString();
        }
    }

    //Query for ui catalog ui policies to get policy actions
    var catpol = new GlideRecord('catalog_ui_policy');
    catpol.addQuery('catalog_item', sysid);
    catpol.query();
    while(catpol.next()){
        //Query for ui policy actions
        var uipact = new GlideRecord('catalog_ui_policy_action');
        uipact.addQuery('ui_policy', catpol.sys_id.toString());
        uipact.query();
        while(uipact.next()){
            //Add the ui policy action sys_id to the ui policy action string
            actID = actID + ',' + uipact.sys_id.toString();
        }
    }

    //Query for variable set relationships
    var vsrel = new GlideRecord('io_set_item');
    vsrel.addQuery('sc_cat_item', sysid);
    vsrel.query();
    while(vsrel.next()){
        //Add the item set relationship sys_id to the item set string
        vsrelID = vsrelID + ',' + vsrel.sys_id.toString();
        //Get the variable set
        var vs = vsrel.variable_set.getRefRecord();
        if(vs){
            //Add the variable set sys_id to the variable set string
            vsID = vsID + ',' + vs.sys_id.toString();
            //Query for variables in the set
            var v = new GlideRecord('item_option_new');
            v.addQuery('variable_set', vs.sys_id);
            v.query();
            while(v.next()){
                //Add the variable sys_id to the variable string
                vID = vID + ',' + v.sys_id.toString();
                //Query for variable question choices
                var vqc = new GlideRecord('question_choice');
                vqc.addQuery('question', v.sys_id.toString());
                vqc.query();
                while(vqc.next()){
                    //Add the variable question sys_id to the variable question string
                    qcID = qcID + ',' + vqc.sys_id.toString();
                }
            }

            //Query for ui policies in the set
            var uip = new GlideRecord('catalog_ui_policy');
            uip.addQuery('variable_set', vs.sys_id.toString());
            uip.query();
            while(uip.next()){
                //Add the ui policy sys_id to the ui policy string
                uipID = uipID + ',' + uip.sys_id.toString();
                //Query for ui policy actions
                var uipa = new GlideRecord('catalog_ui_policy_action');
                uipa.addQuery('ui_policy', uip.sys_id.toString());
                uipa.query();
                while(uipa.next()){
                    //Add the ui policy action sys_id to the ui policy action string
                    actID = actID + ',' + uipa.sys_id.toString();
                }
            }

            //Query for client scripts in the set
            var cs = new GlideRecord('catalog_script_client');
            cs.addQuery('variable_set', vs.sys_id.toString());
            cs.query();
            while(cs.next()){
                //Add the client script sys_id to the client script string
                csID = csID + ',' + cs.sys_id.toString();
            }
        }
    }

    exporter.addQuerySet('sc_catalog', 'sys_idIN' + catalogID);
    exporter.addQuerySet('sc_category', 'sys_idIN' + categoryID);
    exporter.addQuerySet('io_set_item', 'sys_idIN' + vsrelID);
    exporter.addQuerySet('item_option_new_set', 'sys_idIN' + vsID);
    exporter.addQuerySet('item_option_new', 'sys_idIN' + vID);
    exporter.addQuerySet('question_choice', 'sys_idIN' + qcID);
    exporter.addQuerySet('catalog_ui_policy', 'sys_idIN' + uipID);
    exporter.addQuerySet('catalog_ui_policy_action', 'sys_idIN' + actID);
    exporter.addQuerySet('catalog_script_client', 'sys_idIN' + csID);
    exporter.exportRecords(g_response);
})(g_request, g_response, g_processor);
