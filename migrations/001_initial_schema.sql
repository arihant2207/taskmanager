-- ============================================
-- 1. PROFILES TABLE
-- Supabase Auth khud "auth.users" table maintain karta hai (email, id, etc.)
-- but wo table humein directly modify nahi karni chahiye.
-- Isliye ek "profiles" table banate hain jo auth.users se linked hai,
-- taaki hum extra info (name, avatar) store kar sakein aur
-- task assignment ke liye users ki list query kar sakein.
-- ============================================
create table profiles (
  id uuid references auth.users(id) on delete cascade primary key,
  email text not null,
  full_name text,
  avatar_url text,
  created_at timestamptz default now()
);

-- Trigger: jab bhi naya user Google se signup/login kare,
-- automatically ek profile row bhi create ho jaaye
create function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, email, full_name, avatar_url)
  values (
    new.id,
    new.email,
    new.raw_user_meta_data->>'full_name',
    new.raw_user_meta_data->>'avatar_url'
  );
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- ============================================
-- 2. TASKS TABLE
-- ============================================
create type task_status as enum ('todo', 'in_progress', 'done');

create table tasks (
  id uuid default gen_random_uuid() primary key,
  title text not null,
  description text,
  status task_status default 'todo',
  created_by uuid references profiles(id) not null,
  assigned_to uuid references profiles(id),
  created_at timestamptz default now(),
  completed_at timestamptz
);

-- ============================================
-- 3. ROW LEVEL SECURITY (RLS)
-- Ye security ka core hai — bina RLS ke, koi bhi user
-- Supabase client se directly kisi ki bhi tasks read/edit kar sakta hai.
-- ============================================
alter table profiles enable row level security;
alter table tasks enable row level security;

-- Sab logged-in users saare profiles dekh sakein (dropdown ke liye zaroori)
create policy "Profiles are viewable by authenticated users"
  on profiles for select
  using (auth.role() = 'authenticated');

-- Tasks: user sirf wahi tasks dekh sake jo usne banaye ya jo usko assign hue
create policy "Users can view own or assigned tasks"
  on tasks for select
  using (auth.uid() = created_by or auth.uid() = assigned_to);

-- Tasks: sirf logged-in user hi task create kar sake, aur created_by khud hi ho
create policy "Users can create tasks"
  on tasks for insert
  with check (auth.uid() = created_by);

-- Tasks: creator ya assignee hi update kar sake (status change karne ke liye)
create policy "Creator or assignee can update task"
  on tasks for update
  using (auth.uid() = created_by or auth.uid() = assigned_to);