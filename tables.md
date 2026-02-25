-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.blog_posts (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  title text NOT NULL,
  slug text NOT NULL UNIQUE,
  content text NOT NULL DEFAULT ''::text,
  excerpt text NOT NULL DEFAULT ''::text,
  author text NOT NULL DEFAULT ''::text,
  author_bio text NOT NULL DEFAULT ''::text,
  featured_image text,
  published boolean NOT NULL DEFAULT false,
  published_at timestamp with time zone,
  views integer NOT NULL DEFAULT 0,
  tags ARRAY NOT NULL DEFAULT '{}'::text[],
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT blog_posts_pkey PRIMARY KEY (id)
);
CREATE TABLE public.contact_submissions (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  type text NOT NULL,
  name text NOT NULL,
  email text NOT NULL,
  phone text,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT contact_submissions_pkey PRIMARY KEY (id)
);
CREATE TABLE public.destinations (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  name text NOT NULL,
  slug text NOT NULL UNIQUE,
  description text NOT NULL DEFAULT ''::text,
  short_description text NOT NULL DEFAULT ''::text,
  country text NOT NULL DEFAULT ''::text,
  region text NOT NULL DEFAULT ''::text,
  hero_image text,
  images ARRAY NOT NULL DEFAULT '{}'::text[],
  featured boolean NOT NULL DEFAULT false,
  highlights ARRAY NOT NULL DEFAULT '{}'::text[],
  best_time_to_visit text NOT NULL DEFAULT ''::text,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT destinations_pkey PRIMARY KEY (id)
);
CREATE TABLE public.faq (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  question text NOT NULL,
  answer text NOT NULL DEFAULT ''::text,
  category text NOT NULL DEFAULT 'General'::text,
  sort_order integer NOT NULL DEFAULT 0,
  CONSTRAINT faq_pkey PRIMARY KEY (id)
);
CREATE TABLE public.seo_meta (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  page_path text NOT NULL UNIQUE,
  title text NOT NULL DEFAULT ''::text,
  description text NOT NULL DEFAULT ''::text,
  og_title text,
  og_description text,
  og_image text,
  canonical_url text,
  no_index boolean NOT NULL DEFAULT false,
  json_ld jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT seo_meta_pkey PRIMARY KEY (id)
);
CREATE TABLE public.site_settings (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  key text NOT NULL UNIQUE,
  value jsonb NOT NULL DEFAULT '""'::jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT site_settings_pkey PRIMARY KEY (id)
);
CREATE TABLE public.testimonials (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  name text NOT NULL,
  location text NOT NULL DEFAULT ''::text,
  rating integer NOT NULL DEFAULT 5,
  text text NOT NULL DEFAULT ''::text,
  tour text,
  avatar text,
  date date NOT NULL DEFAULT CURRENT_DATE,
  CONSTRAINT testimonials_pkey PRIMARY KEY (id)
);
CREATE TABLE public.tour_destinations (
  tour_id bigint NOT NULL,
  destination_id bigint NOT NULL,
  CONSTRAINT tour_destinations_pkey PRIMARY KEY (tour_id, destination_id),
  CONSTRAINT tour_destinations_tour_id_fkey FOREIGN KEY (tour_id) REFERENCES public.tours(id),
  CONSTRAINT tour_destinations_destination_id_fkey FOREIGN KEY (destination_id) REFERENCES public.destinations(id)
);
CREATE TABLE public.tours (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  title text NOT NULL,
  slug text NOT NULL UNIQUE,
  description text NOT NULL DEFAULT ''::text,
  short_description text NOT NULL DEFAULT ''::text,
  duration_days integer NOT NULL DEFAULT 1,
  price numeric NOT NULL DEFAULT 0,
  original_price numeric,
  currency text NOT NULL DEFAULT 'USD'::text,
  category text NOT NULL DEFAULT ''::text,
  featured boolean NOT NULL DEFAULT false,
  customizable boolean NOT NULL DEFAULT false,
  highlights ARRAY NOT NULL DEFAULT '{}'::text[],
  itinerary jsonb NOT NULL DEFAULT '[]'::jsonb,
  images ARRAY NOT NULL DEFAULT '{}'::text[],
  hero_image text,
  seo_title text,
  seo_description text,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT tours_pkey PRIMARY KEY (id)
);
CREATE TABLE public.travel_styles (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  name text NOT NULL,
  slug text NOT NULL UNIQUE,
  description text NOT NULL DEFAULT ''::text,
  icon text NOT NULL DEFAULT ''::text,
  image text,
  CONSTRAINT travel_styles_pkey PRIMARY KEY (id)
);