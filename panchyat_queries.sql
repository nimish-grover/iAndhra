--population census
select sum(pc.population_count) as population_count, population_id,tj.panchayat_id as territory_id from population_census pc 
inner join territory_joins tj on tj.id = pc.territory_id 
group by tj.panchayat_id,pc.population_id
order by tj.panchayat_id


-- livestock census data
SELECT lc.livestock_id,sum(lc.livestock_count) as livstock_count,lc.block_code,lc.district_code,lc.panchayat_code,tj.panchayat_id as tj_id FROM public.livestock_census AS lc
inner join territory_joins tj on tj.id = lc.tj_id
group by lc.livestock_id, lc.panchayat_code,lc.block_code,lc.district_code,tj.panchayat_id  

--crop census data
SELECT sum(cc.crop_area) as crop_area,cc.crop_id,tj.panchayat_id as territory_id, p.lgd_code as panchayat_lgd_code FROM public.crop_census AS cc
inner join territory_joins tj on tj.id = cc.territory_id
inner join panchayats p on p.id = tj.panchayat_id
group by tj.panchayat_id,cc.crop_id,p.lgd_code
order by tj.panchayat_id 

--waterbody census
SELECT sum(wc.spread_area) as spread_area,sum(wc.storage_capacity) as storage_capacity ,sum(max_depth) as max_depth,wc.waterbody_id,wc.district_code,
tj.panchayat_id as tj_id,p.lgd_code as panchayat_code FROM public.waterbodies_census AS wc
inner join territory_joins tj on tj.id = wc.tj_id
inner join panchayats p on p.id = tj.panchayat_id
group by wc.waterbody_id, tj.panchayat_id, p.lgd_code, wc.district_code
order by tj.panchayat_id

--groundwater census
SELECT AVG(ge.stage_of_extraction) as stage_of_extraction,AVG(ge.rainfall) as rainfall,AVG(ge.recharge) as recharge,AVG(ge.discharge) as discharge,
AVG(ge.extractable) as exctractable,AVG(ge.extraction) as extraction,
tj.panchayat_id,tj.block_id ,tj.district_id ,tj.panchayat_id as tj_id 
FROM public.groundwater_extractions AS ge
inner join territory_joins tj on tj.id = ge.tj_id
group by tj.panchayat_id,tj.block_id,tj.district_id
order by tj.panchayat_id 

--lulc census 
SELECT sum(lc.lulc_area) as lulc_area,lc.lulc_id,tj.panchayat_id as tj_id  FROM public.lulc_census AS lc
inner join territory_joins tj on tj.id = lc.tj_id
group by lc.lulc_id,tj.panchayat_id
order by tj.panchayat_id 

