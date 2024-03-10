SELECT 
    root.project,
    root.id AS root_id,
    COUNT(DISTINCT branch.id) AS branch_count,
    ARRAY_AGG(DISTINCT jsonb_extract_path_text(leaf.extra, 'color')) FILTER (WHERE jsonb_extract_path_text(leaf.extra, 'color') IS NOT NULL) AS leaf_colors
FROM 
    A AS root
LEFT JOIN 
    A AS branch ON root.id = branch.parent_id AND branch.type = 'branch'
LEFT JOIN 
    A AS leaf ON branch.id = leaf.parent_id AND leaf.type = 'leaf'
WHERE 
    root.type = 'root'
    AND root.project = 1
GROUP BY 
    root.project,
    root.id
ORDER BY 
    root.id;
