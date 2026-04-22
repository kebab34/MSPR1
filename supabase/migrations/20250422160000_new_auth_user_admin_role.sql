-- Nouveaux comptes Auth : rôle application admin + plan freemium (démo / accès back-office)

CREATE OR REPLACE FUNCTION public.handle_new_auth_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF NEW.email IS NULL THEN
    RETURN NEW;
  END IF;

  INSERT INTO public.utilisateurs (
    email,
    auth_id,
    app_role,
    type_abonnement,
    nom,
    prenom
  )
  VALUES (
    NEW.email,
    NEW.id,
    'admin',
    'freemium',
    NULLIF(TRIM(NEW.raw_user_meta_data ->> 'nom'), ''),
    NULLIF(TRIM(NEW.raw_user_meta_data ->> 'prenom'), '')
  )
  ON CONFLICT (email) DO UPDATE
    SET
      auth_id = EXCLUDED.auth_id,
      nom = COALESCE(EXCLUDED.nom, public.utilisateurs.nom),
      prenom = COALESCE(EXCLUDED.prenom, public.utilisateurs.prenom),
      updated_at = now();

  RETURN NEW;
END;
$$;
